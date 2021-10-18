$(document).ready(function(){
    var total_price = 0;
    var total_units = 0;
    var subtotals = ""
    $(".shopping-movie-info-container").each(function() {
        var price = parseFloat($(this).find(".unitprice").text())
        var units = parseInt($(this).find(".units").text())
        var subt = price*units
        total_price += subt
        total_units += units
        subtotals += "<tr><th class=\"movie-info-a\">"+ subt.toFixed(2) +"€</th></tr>"
    })
    $(".total-units").html(total_units)
    $(".subtotal").html(subtotals)
    $(".total").html(total_price.toFixed(2))
    
})