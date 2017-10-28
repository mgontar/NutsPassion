library(shiny)
library(dplyr)
library(ggplot2)
library(scales)

# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  # Executed once, as application starts
  prod <- read.csv(url("https://raw.githubusercontent.com/mgontar/NutsPassion/master/data/output/data_price.csv"))
  nutr <- read.csv(url("https://raw.githubusercontent.com/mgontar/NutsPassion/master/data/output/data_pivot.csv"))
  rda_pre <- read.csv(url("https://raw.githubusercontent.com/mgontar/NutsPassion/master/data/output/data_rda.csv"))
  
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
    rda <- rda_pre %>% pull(rda)
    mda <- rda_pre %>% pull(mda)
    
    list(price = price, nutr = nutr, mda = mda, rda = rda, name_prod = name_prod)
  }) 
  
  # Apply simplex model to the data provided
  applySimplex <- reactive({
    dataSource <- readData()
    price_disturbance <- 1 + rnorm(n = length(dataSource$price), mean = 0, sd = input$price_volatility/100) # conv from % to fracction of unit 
    result <- boot::simplex(a = dataSource$price*price_disturbance, 
                            A1 = rbind(dataSource$nutr,diag(length(dataSource$price))), 
                            b1 = c(dataSource$mda,rep(input$product_boundary/1000, length(dataSource$price))), 
                            A2 = dataSource$nutr, 
                            b2 = dataSource$rda)
    
    res <- result$soln
    names(res) <- dataSource$name_prod
    res <- as.data.frame(cbind(product = dataSource$name_prod, units = res, unit_price = dataSource$price))
    res$product <- as.character(res$product)
    res$units <- as.numeric(as.character(res$units))
    res$unit_price <- as.numeric(as.character(res$unit_price))
    res <- res[res$units>0,] %>% arrange(desc(units*unit_price))
    res$product <- factor(res$product, levels = res$product)
    
    res
  })
  
  
  # Generation of plot
  output$dietPlot <- renderPlot({
    res <- applySimplex()
    gg <- ggplot(res, aes(x = "", y = units*unit_price, fill = product)) + 
      geom_bar(width = 1, stat = "identity") + 
      theme_void() + 
      coord_polar("y", start = 0) +
      theme(axis.text.x = element_blank()) +
      ggtitle(paste0(round(sum(res$units*res$unit_price), digits = 2),"UAH (", round(sum(res$units*res$unit_price)*0.037, digits = 2),  "$) daily basket cost distribution")) +
      theme(plot.title = element_text(hjust = 0.5, size = 24, face = "bold"))
    
    plot(gg)
  })
  
  output$dietTable <- renderTable({
    res <- applySimplex()
    res <- res %>% mutate(price_per_product = units*unit_price, units = as.integer(round(units*1000)))
    names(res) <- c("Product", "Weight, g", "Price per kg (UAH)", "Price of given product (UAH)")
    res
  })
  
})
