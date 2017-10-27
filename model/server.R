library(shiny)
library(dplyr)
library(ggplot2)
library(scales)

# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  # Executed once, as application starts
  prod <- read.csv(url("https://raw.githubusercontent.com/mgontar/NutsPassion/master/shinyApp/data_snapshot/products.csv"))
  nutr <- read.csv(url("https://raw.githubusercontent.com/mgontar/NutsPassion/master/shinyApp/data_snapshot/matrix.csv"))
  rda_pre <- read.csv(url("https://raw.githubusercontent.com/mgontar/NutsPassion/master/shinyApp/data_snapshot/rda.csv"))
  
  #Executed on each update of parameters
  readData <- reactive({
    prod_wr <- input$prices_vector
    nutr_wr <- input$nutrition_matrix
    rda_wr <- input$rda_vectors
    
    if(!is.null(prod_wr)) prod <- read.csv(prod_wr$datapath)
    if(!is.null(nutr_wr)) nutr <- read.csv(nutr_wr$datapath)
    if(!is.null(rda_wr)) rda_pre <- read.csv(rda_wr$datapath)
    
    name_prod <- as.character(prod[,1])
    price <- prod[,2]
    nutr <- as.matrix(nutr[,-1])
    rda <- rda_pre[,2]
    mda <- rda_pre[,3]
    
    list(price = price, nutr = nutr, mda = mda, rda = rda, name_prod = name_prod)
  }) 
  
  # Apply simplex model to the data provided
  applySimplex <- reactive({
    dataSource <- readData()
    price_disturbance <- 1 + rnorm(n = length(dataSource$price), mean = 0, sd = input$price_volatility/100) # conv from % to fracction of unit 
    result <- boot::simplex(a = dataSource$price*price_disturbance, A1 = dataSource$nutr, b1 = dataSource$mda, A2 = dataSource$nutr, b2 = dataSource$rda)
    
    res <- result$soln
    names(res) <- dataSource$name_prod
    res <- as.data.frame(cbind(name = dataSource$name_prod, value = res))
    res$name <- as.character(res$name)
    res$value <- as.numeric(as.character(res$value))
    res <- res[res$value>0,]
    
    res
  })
  
  
  # Generation of plot
  output$dietTable <- renderPlot({
    res <- applySimplex()
    gg <- ggplot(res, aes(x = "", y = value, fill = name)) + 
      geom_bar(width = 1, stat = "identity") + 
      theme_void() + 
      coord_polar("y", start = 0) +
      theme(axis.text.x = element_blank()) +
      geom_text(aes(y = value/3 + c(0, cumsum(value)[-length(value)]),
                    label = percent(value/100)), size = 5)
    
    plot(gg)
  })
  
})
