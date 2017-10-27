library(shiny)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
  
  # Application title
  titlePanel("Optimal diet"),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    sidebarPanel(
      fileInput("prices_vector", "Prices",
                accept = c(
                  "text/csv",
                  "text/comma-separated-values,text/plain",
                  ".csv")),
      fileInput("nutrition_matrix", "Nutrition",
                accept = c(
                  "text/csv",
                  "text/comma-separated-values,text/plain",
                  ".csv")),
      fileInput("rda_vectors", "Norms",
                accept = c(
                  "text/csv",
                  "text/comma-separated-values,text/plain",
                  ".csv")),
      sliderInput("price_volatility", "Price volatility, %",
                  min = 0, max = 10, value = 0, step = 1),
      submitButton("Run")
    ),
    
    
    # Show a plot of the generated distribution
    mainPanel(
      plotOutput("dietTable")
    )
  )
))
