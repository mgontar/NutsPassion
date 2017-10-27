library(dplyr)
library(boot)

#load data
prod <- read.csv('data_price.csv')
nutr <- read.csv('data_pivot.csv')
rda_pre <- read.csv('data_rda.csv')
  
#reshape data
price <- prod[,2]
nutr <- as.matrix(nutr[,-1])
rda <- rda_pre[,'rda']
mda <- rda_pre[,'mda']

#MINIMAL SOLUTION

#simplex method
model <- simplex(a = price, 
                 A1 = nutr, b1 = mda, 
                 A2 = nutr, b2 = rda)


results <- as.data.frame(cbind(prod, minimal_solution = model$soln))
budget <- model$value
nutrients <- as.data.frame(cbind(rda_pre[,c('eng_name','rda')], minimal_solution = nutr %*% as.matrix(model$soln)))

#results<-results[results$value>0,]


#SOLUTION WITH COSTRAINT ON PRODUCTS

model <- simplex(a = price, 
                 A1 = rbind(nutr,diag(length(price))), 
                 b1 = rbind(as.matrix(mda), as.matrix(rep(0.25,length(price)))), 
                 A2 = nutr, b2 = rda)


results <- as.data.frame(cbind(prod, minimal_solution = model$soln))
budget <- model$value
nutrients <- as.data.frame(cbind(rda_pre[,c('eng_name','rda')], minimal_solution = nutr %*% as.matrix(model$soln)))


#MANY SOLUTIONS
for (i in 1:1000){
  print(i)
  price_disturbance <- 1 + rnorm(n = length(price), mean = 0, sd = 0.25) 
  
  model <- simplex(a = price * price_disturbance, 
                   A1 = rbind(nutr,diag(length(price))), 
                   b1 = rbind(as.matrix(mda), as.matrix(rep(0.25,length(price)))), 
                   A2 = nutr, b2 = rda)
  
  results <- cbind(results,solution = model$soln)
  
  nutrients <- as.data.frame(cbind(nutrients, 
                                   minimal_solution = nutr %*% as.matrix(model$soln)))
 
}


#FIND MOST DISTINCT SOLUTIONS
results_distinct <- results[,c(1,2,3)]
  
for (i in 4:(dim(results)[2])){
  solution <- results[,i]
  
    min = 100000
  for (j in 3:(dim(results_distinct)[2])){
    distance = sum((solution-results_distinct[,j])^2)
    if (distance < min) {min = distance}
  }
    
  if (min > 0.28) {
    results_distinct <- cbind(results_distinct,solution)
  }
  
}


#CALCULARE CHARACTERISTICS
budgets <- cbind(NA,NA)
for (i in 3:dim(results_distinct)[2]){
  budgets <- cbind(budgets, sum(results_distinct[,2]*results_distinct[,i]))
}

weight <- t(as.matrix(c(NA,NA,colSums(results_distinct[,-c(1,2)]))))
colnames(budgets) <- colnames(results_distinct)
colnames(weight) <- colnames(results_distinct)
final_results <- rbind(results_distinct, as.matrix(budgets))
final_results$name_prep_eng <- as.character(final_results$name_prep_eng)
final_results[dim(final_results)[1],1] <- 'Basket Price, UAH'
final_results <- rbind(final_results, weight)
final_results[dim(final_results)[1],1] <- 'Basket Price, kg'


nutrients_avg <- cbind(nutrients[,c(1,2)], data.frame(mean = rowMeans(nutrients[,-c(1,2)])))

#WRITE INTO FILES

write.csv(final_results,'baskets.csv', na='', row.names = FALSE)
write.csv(nutrients_avg,'nutrients.csv', na='', row.names = FALSE)


