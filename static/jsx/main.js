/** @jsx React.DOM */

var DynamicSearch = React.createClass({

  // sets initial state
  getInitialState: function(){
    return { searchString: '', data: []};
  },

  // sets state, triggers render method
  handleChange: function(event){
    // grab value form input box
    this.setState({searchString:event.target.value});
    // console.log("scope updated!")
  },

  componentDidMount: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data_in) {
        console.log("Loaded data", data_in)
        this.setState({data: data_in});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },

  render: function() {

    var lunches = this.state.data;
    console.log("Lunches var is " + lunches)
    var searchString = this.state.searchString.trim().toLowerCase();

    // filter countries list by value from input box
    if(searchString.length > 0){
      lunches = lunches.filter(function(lunch){
        return lunch.submitter.toLowerCase().match( searchString );
      });
    }
    return (
      <div>
        <input type="text" value={this.state.searchString} onChange={this.handleChange} placeholder="Google!" />
        <ul>
          {
             lunches.map(
                function(lunch){
                    var submitter = <span style={{color: 'red'}}> {lunch.submitter} </span>
                    var food = <span style={{color: 'orange'}}> {lunch.food} </span>
                    return <strong><li><td>{submitter}</td> just ate <td>{food}</td></li></strong>
                }
             )
          }
        </ul>
      </div>
    )
  }
});


React.render(
  <DynamicSearch url="/lunches" />,
  document.getElementById('lunches')
);
