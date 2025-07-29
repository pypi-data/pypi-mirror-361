HTML_TEMPLATE = r"""<html></html>
<head>
    <style type="text/css">
        #mySvgId {
            height: 90%;
            width: 90%;
        }
    </style>
    <title>Dependency Diagram</title>
</head>
<body>
    <div id="graphDiv"></div>
    <button id="downloadButton">Download SVG</button>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.5.0/dist/svg-pan-zoom.min.js"></script>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.esm.min.mjs';
        mermaid.initialize({
            startOnLoad:true,
            sequence:{
                    useMaxWidth:false
            }
        });

        const drawDiagram = async function () {
            const element = document.querySelector('#graphDiv');
            const graphDefinition = `
            {{diagram_definition}}
`;
            const { svg } = await mermaid.render('mySvgId', graphDefinition);
            element.innerHTML = svg.replace(/[ ]*max-width:[ 0-9\.]*px;/i , '');
            var panZoomTiger = svgPanZoom('#mySvgId', {
                zoomEnabled: true,
                controlIconsEnabled: true,
                fit: true,
                center: true
            })
        };
        await drawDiagram();

        // Add event listener to the download button to download the SVG without the pan & zoom buttons
        document.getElementById('downloadButton').addEventListener('click', function() {
            const svg = document.querySelector('#mySvgId');
            let svgData = new XMLSerializer().serializeToString(svg);
            
            // To remove the pan & zoom buttons of the diagram, any element whose class contains the string 'svg-pan-zoom-*' should be removed
            svgData = svgData.replace(/<g\b[^>]*\bclass="svg-pan-zoom-.*?".*?>.*?<\/g>/g, '');
            // The above leaves out a closing </g> tag before the final </svg> tag, so we need to remove it
            svgData = svgData.replace(/<\/g><\/svg>/, '</svg>');

            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const svgUrl = URL.createObjectURL(svgBlob);
            const downloadLink = document.createElement('a');
            downloadLink.href = svgUrl;
            downloadLink.download = 'diagram.svg';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });
    </script>
  </body>
</html>"""
