
$(document).ready(function() {
    $(this).find(".purchase-history").slideToggle(0)
    $(".purchase-date").click(function() {
        $(this).siblings(".purchase-history").slideToggle(700)
    })
})

$(document).ready(function() {
    $(".history-purchase").each(function() {
        var total_price = 0;
        $(this).find(".purchase-table").each(function() {
            var price = parseFloat($(this).find(".unitprice").text())
            var units = parseInt($(this).find(".units").text())
            var subtotal = price*units
            total_price += subtotal
            $(this).find(".subtotal").html(subtotal.toFixed(2))
        })
        $(this).find(".total").html(total_price.toFixed(2))
    })
})