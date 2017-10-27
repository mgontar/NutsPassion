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
      sliderInput("price_disturb", "Price disturbance",
                  min = 0, max = 0.1, value = 0, step = 0.01),
      submitButton("Run")
    ),
    
    
    # Show a plot of the generated distribution
    mainPanel(
      plotOutput("dietTable")
    )
  )
))
