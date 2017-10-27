library(shiny)
library(dplyr)
library(ggplot2)
library(scales)

# Define server logic required to draw a histogram
shinyServer(function(input, output) {
  readData <- reactive({
    prod_wr <- input$prices_vector
    nutr_wr <- input$nutrition_matrix
    rda_wr <- input$rda_vectors
    
    if(!is.null(prod_wr)) prod <- read.csv(prod_wr$datapath)
    if(!is.null(nutr_wr)) nutr <- read.csv(nutr_wr$datapath)
    if(!is.null(rda_wr)) rda_pre <- read.csv(rda_wr$datapath)
    
    name_prod <- as.character(prod$name_prep_eng)
    price <- prod %>% select(price_kg_uah)
    price <- as.numeric(price[,1])
    
    nutr <- nutr %>% select(-eng_name) %>% as.matrix()
    
    rda <- rda_pre %>% select(rda)
    rda <- as.numeric(rda[,1])
    mda <- rda_pre %>% select(mda)
    mda <- as.numeric(mda[,1])
    
    list(price = price, nutr = nutr, mda = mda, rda = rda, name_prod = name_prod)
  }) 
  
  output$dietTable <- renderPlot({
    dataSource <- readData()
    result <- boot::simplex(a = dataSource$price, A1 = dataSource$nutr, b1 = dataSource$mda, A2 = dataSource$nutr, b2 = dataSource$rda)
    res <- result$soln
    names(res) <- dataSource$name_prod
    res <- as.data.frame(cbind(name = dataSource$name_prod, value = res))
    res$name <- as.character(res$name)
    res$value <- as.numeric(as.character(res$value))
    res <- res[res$value>0,]
    
    gg <- ggplot(res, aes(x = "", y = value, fill = name)) + 
      geom_bar(width = 1, stat = "identity") + 
      coord_polar("y", start = 0) +
      scale_fill_ger
      theme(axis.text.x = element_blank()) +
      geom_text(aes(y = value/3 + c(0, cumsum(value)[-length(value)]),
                    label = percent(value/100)), size = 5)
    
    plot(gg)
  })
  
})
