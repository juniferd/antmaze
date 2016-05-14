var statsControl = document.getElementById('stats-control')

statsControl.addEventListener('click', function(e){
    controlClass = statsControl.className
    statsPanel = document.getElementById('stats-panel')

    if (controlClass == 'expand') {
        statsPanel.className = 'expanded'
        statsControl.className = 'collapse'
        document.getElementById('content').className = 'sidebar-expanded'
    } else if (controlClass == 'collapse') {
        statsPanel.className = 'collapsed'
        statsControl.className = 'expand'
        document.getElementById('content').className = 'sidebar-collapsed'
    }
});

var foodLink = document.getElementById('food-link-tip');

foodLink.addEventListener('click', function(e){
    e.preventDefault();
})
foodLink.addEventListener('mouseover',function(e){
    
    foodTip.style('visibility','visible')
        .style('opacity','1')
        .style("top",function(){
            var docTop = document.getElementById('content').scrollTop
            var thisTop = parseInt(d3.select('.food').attr('y'))
            var finalTop = thisTop - docTop + 55
            return finalTop+'px'
        })
        .style("left",function(){
            var farmLeft = document.getElementById('antfarm').getBoundingClientRect().left
            var thisLeft = parseInt(d3.select('.food').attr('x'))
            console.log(farmLeft,thisLeft)
            var finalLeft = farmLeft + thisLeft - 55
            return finalLeft+'px'
        });
});
foodLink.addEventListener('mouseout',function(e){
    foodTip.style('opacity','0')
                .style('visibility','hidden')
                .style('pointer-events', 'none');
})