// Função para gerar um gráfico de linhas
function lineChart(data, panel) {
	// set the dimensions and margins of the graph
	var margin = {top: 40, right: 50, bottom: 40, left: 50},
	    width = 960 - margin.left - margin.right,
	    height = 500 - margin.top - margin.bottom;

	// parse the date / time
	var parseTime = d3.timeParse("%M:%S");

	// set the ranges
	var x = d3.scaleTime().range([0, width]);
	var y = d3.scaleLinear().range([height, 0]);

	// define the 1st line
	var valueline = d3.line()
	    .x(function(d) { return x(d.date); })
	    .y(function(d) { return y(d.close); });

	// define the 2nd line
	var valueline2 = d3.line()
	    .x(function(d) { return x(d.date); })
	    .y(function(d) { return y(d.open); });

	// define the 3nd line
	var valueline3 = d3.line()
	    .x(function(d) { return x(d.date); })
	    .y(function(d) { return y(d.terc); });

	// append the svg obgect to the body of the page
	var svg = d3.select(panel).append("svg")
		    .attr("width", width + margin.left + margin.right)
		    .attr("height", height + margin.top + margin.bottom)
		  .append("g")
		    .attr("transform",
		          "translate(" + margin.left + "," + margin.top + ")");

	// format the data
	data.forEach(function(d) {
	  d.date = parseTime(d.date);
	  d.close = +d.close;
	  d.open = +d.open;
	  d.terc = +d.terc;
	});

	// Scale the range of the data
	x.domain(d3.extent(data, function(d) { return d.date; }));
	y.domain([0, d3.max(data, function(d) { return Math.max(d.close, d.open); })]);

	// Add the valueline path.
	svg.append("path")
	  .data([data])
	  .attr("class", "line")
	  .style("stroke", "#00aedb")
	  .attr("d", valueline);

	// Add the valueline2 path.
	svg.append("path")
	  .data([data])
	  .attr("class", "line")
	  .style("stroke", "#d11141")
	  .attr("d", valueline2);

	// Add the valueline3 path.
	svg.append("path")
	  .data([data])
	  .attr("class", "line")
	  .style("stroke", "#00b159")
	  .attr("d", valueline3);

	let xAxis = d3.axisBottom()
	      .scale(x)
	      .tickFormat(d3.timeFormat("%M:%S"));;

	let yAxis = d3.axisLeft()
	    	.scale(y);

	svg.append("g")			
	.attr("class", "grid")
	.attr("transform", "translate(0," + height + ")")
	.call(d3.axisBottom(x)
			.ticks(5)
			.tickSize(-height)
			.tickFormat(""))

	svg.append("g")			
	.attr("class", "grid")
	.call(d3.axisLeft(y)
			.ticks(5)
			.tickSize(-width)
			.tickFormat(""))

	// Caixa de Legenda
	var legendColorScale = d3.scaleOrdinal()
						 .range(["#00aedb", "#d11141", "#00b159"])

	var legend = svg.append("g")
				.attr("class", "legend")
				.style("margin", "5px 5px 5px 5px")
				.style("background-color", "#222222FF")
				.attr("font-family", "Roboto")
				.attr("font-size", 12)
				.attr("text-anchor", "left")
				.selectAll("g")
				.data(["Veículo Leve", "Veículo de Passeio", "Veículo Pesado"])
				.enter().append("g")
				.attr("transform", function(d, i) { return "translate(0," + i * 25 + ")"; });

	legend.append("circle")
		.attr("cx", width - 145)
		.attr("cy", 10)
		.attr("r", 10)
		.attr("fill", legendColorScale);

	legend.append("text")
		.attr("font-family", "Roboto")
		.attr("font-size", 12)
		.attr("x", width - 125)
		.attr("y", 9.5)
		.attr("dy", "0.32em")
		.text(function(d) { return d; });


	// Adiciona os eixos à região do gráfico
	svg.append("g")
		.attr("transform", "translate(0,"+ height + ")")
		.attr("class", "axis")
		.call(xAxis)	

	svg.append("g")
		.attr("class", "axis")
		.call(yAxis)

	svg.append("text")
		.attr("transform", "rotate(-90)")
		.attr("y", 0 - margin.left)
		.attr("x", 0 - (height / 2))
		.attr("dy", "1em")
		.style("text-anchor", "middle")
		.attr("font-family", "Roboto")
		.attr("font-size", "14px")
		.text("Contagem");
}

function barChart(dataset, panel) {

	// Variáveis Gerais
	var margin = {top: 60, right: 50, bottom: 40, left: 50},
	    w = 960 - margin.left - margin.right,
	    h = 500 - margin.top - margin.bottom;

	var label = dataset[0]
	var dataset = dataset[1]

	console.log(d3.max(dataset)+2)

	// Declaração das Funções de Escala
	var xLinScale = d3.scaleLinear()
					.range([0, w])            
					.domain([0, w]);

	var xScale = d3.scaleBand()
					.range([0, w])            
					.domain(label)
					.padding(0.2);

	let yScale = d3.scaleLinear()
					.domain([0, d3.max(dataset)+2])
					.range([h, 0]);	

	colorScale = d3.scaleOrdinal()
					.domain(label)
					.range(["#00aedb", "#d11141", "#00b159"])

	// Declaração dos Eixos
	let xAxis = d3.axisBottom()
					.scale(xScale);
	
	let yAxis = d3.axisLeft()
					.scale(yScale).ticks(5).tickSize(-w);

	// Declara a região onde os gráficos serão desenhados
	var svg = d3.select(panel).append("svg")
								.attr("width", w + margin.left + margin.right)
								.attr("height", h + margin.top + margin.bottom)
							.append("g")
								.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
 
	// Cria as labels com texto da variável numérica das barras
	svg.selectAll()
		.data(dataset)
		.enter()
			.append("text")
			.attr("id", function(d,i) { console.log(i); return "" + label[i].replace(/ /g, "_")  + "_" + Math.floor(+d) })
			.attr("transform", function(d,i) {
				return "translate(" + (xScale(label[i])+xScale.bandwidth()/2) + "," + (yScale(+d)-10) + ")"
			})
			.style("text-anchor", "middle")
			.attr("font-family", "Roboto")
			.attr("font-size", "18px")
			.style("opacity", 0)
			.text(function(d) { return Number((d).toPrecision(4)) } );

 	// Declara e posiciona os marcadores do gráfico barChart
	var barChart = svg.selectAll()
					.data(dataset)
					  .enter()
					  .append("rect")
					  .attr("x", function(d, i) { return xScale(label[i]) })
					  .attr("y", function(d) { return yScale(d) })
					  .attr("height", function(d) { return h - yScale(d) })
					  .attr("width", xScale.bandwidth())
					  .attr("stroke", "#2F2F2F")
					  .attr("stroke-width", 0)
					  .attr("fill", function(d, i) { return colorScale(label[i]) })
					  .on('mouseenter', function (d, i) {
						d3.select(this).transition().duration(200)
					  		.attr("stroke-width", 2)

					  	d3.select("#"+ label[i].replace(/ /g, "_")  +"_"+Math.floor(d)).transition().duration(200)
					  		.style("opacity", .9)

					  })
					  .on('mouseleave', function (d, i) {
					  	d3.select(this).transition().duration(200)
					  		.attr("stroke-width", 0)

					  	d3.select("#"+ label[i].replace(/ /g, "_") +"_"+Math.floor(d)).transition().duration(500)
					  		.style("opacity", 0)
					  })
	
	// Título do Gráfico e nome dos eixos
	svg.append("g").attr("transform", "translate(0," + h + ")")
					.call(xAxis)
					.selectAll("text")  
						.style("text-anchor", "middle")
						.attr("font-family", "Roboto")
						.attr("font-size", "18px")

}