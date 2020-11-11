const SUBMIT_BTN_INIT_TEXT = "Go!"
const SUBMIT_BTN_LOADING_TEXT = "Loading..."
var artist
socket = io("wss://"+window.location.hostname+"/discography")
socket.on("release_rows", function(data) {
  console.log("release_rows")
  init_disco(true)
  $("#disco").append(data)
})

socket.on("complete", function() {
  console.log("complete")
  $("#loading").hide()
  makeTableSortable(true)
  init_disco(false) // cover the case of 0 rows
})

function correctButtonEnablement() {
  $("#submit").prop('disabled', $("#artist").val().length == 0)
}

function get_discography(e) {
  e.preventDefault()
  artist = $("#artist").val()
  let btnText = $("#submit").html()
  $("#submit").html(SUBMIT_BTN_LOADING_TEXT)
  $("#submit").prop('disabled', true)
  $("#artist-container").hide()
  $("#disco-container").hide()
  $("#disco").empty()
  $("#loading").show()
  console.log("socket emit get '"+artist+"'")
  socket.emit("get", artist)
  return false;
}

/*
 * Initialize the discography display area
 *
 * results_found: boolean indicating if results were found
*/
function init_disco(results_found) {
  if ($("#submit").prop('disabled') == false) {
    return false
  }
  if (results_found) {
    $("#results-heading").html("Complete Discography for "+artist)
    makeTableSortable(false)
    $("#disco-table").show()
  } else {
    $("#results-heading").html("No results found.")
    $("#disco-table").hide()
  }
  $("#submit").html(SUBMIT_BTN_INIT_TEXT)
  $("#submit").prop('disabled', false)
  $("#disco-container").show()
}

function makeTableSortable(enable=false) {
  $("#disco-head tr th").each(function() {
    $(this).attr("data-sortable", enable) // css looks at this value
    $(this).removeAttr("data-sorted")
    $(this).removeAttr("data-sorted-direction")
  })

  if (enable) {
    $("#disco-table").removeAttr("data-sortable-initialized")
    Sortable.init()
  } else { 
    // remove event listeners!
    $("#disco-head").html($("#disco-head").html())
  }
}

$(function () {
  $("#artist").on('input', correctButtonEnablement)
  correctButtonEnablement()
})