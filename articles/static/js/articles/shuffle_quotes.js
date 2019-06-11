 /*
  * Functions to shuffle quotes on individual article pages
  *
  * MJB 6/2019
  */

function shuffle_quotes() {
    // Shuffle quotes - called from shuffle quotes button

    // Get quotes elements
    var quotes_wrapper = document.getElementsByClassName("stock_quotes");
    var stock_quotes = quotes_wrapper[0].children;
    var elements = document.createDocumentFragment();

    // Copy and shuffle quotes
    for (var arr=[],i=0; i<stock_quotes.length; ++i) arr[i]=i;
    arr = shuffle(arr);
    arr.forEach(function(idx) {
        elements.appendChild(stock_quotes[idx].cloneNode(true));
    });

    // Replace orig quotes with shuffled quotes
    quotes_wrapper[0].innerHTML = null;
    quotes_wrapper[0].appendChild(elements);
}

function shuffle(array) {
    // http://stackoverflow.com/questions/962802#962890
    // Shuffle array
    var tmp, current, top = array.length;
    if(top) while(--top) {
      current = Math.floor(Math.random() * (top + 1));
      tmp = array[current];
      array[current] = array[top];
      array[top] = tmp;
    }
    return array;
}
