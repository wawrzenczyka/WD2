function customStartIntro(){
    var intro = introJs();
      intro.setOption('tooltipClass', 'customDefault') //custom buttons and general layout of tooltip
      intro.setOptions({
        steps: [
          {
            element: '#year-slider',
            intro: "Woah <b>slider</b>",
            position: 'right'
          },
          {
            element: '#map-filters',
            intro: "Dwa <i>checkboxy</i>? Tyle możliwości...",
            position: 'right'
          },
          {
            element: '#map',
            intro: '<span style="color: red;">M</span><span style="color: green;">a</span><span style="color: blue;">p</span></span><span style="color: pink;">a</span> :O',
            position: 'right'
          },
          {
            element: '#timeline',
            intro: "<span style='font-family: Comic Sans MS'>O ja cie zmienia się</span>",
            position: 'left'
          },
          {
            element: '#pkd-tree',
            intro: '<strong>Ale fajna drzewomapa</strong>',
            position: 'top'
          }
        ]
      });

      intro.start();
  }