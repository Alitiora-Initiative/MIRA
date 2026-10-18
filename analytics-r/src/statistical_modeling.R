# Statistical Modeling Service
# HTTP API for statistical analysis, GARCH volatility forecasting, and time-series modeling

library(plumber)
library(jsonlite)
library(rugarch)
library(forecast)
library(tseries)
library(quantreg)

# Initialize Plumber
pr <- plumb()

# Forecast volatility using GARCH model
pr$post("/forecast/volatility", function(req) {
  tryCatch({
    data <- fromJSON(req$postBody)
    returns <- data$returns
    horizon <- ifelse(is.null(data$horizon), 7, data$horizon)
    model_type <- ifelse(is.null(data$model), "sGARCH", data$model)

    # Fit GARCH model
    spec <- ugarchspec(
      variance.model = list(model = model_type, garchOrder = c(1, 1)),
      mean.model = list(armaOrder = c(0, 0)),
      distribution.model = "std"
    )

    fit <- ugarchfit(spec = spec, data = returns)

    # Forecast
    forecast <- ugarchforecast(fit, n.ahead = horizon)

    # Extract results
    sigma_forecast <- sigma(forecast)
    conditional_var <- sigma_forecast^2

    list(
      success = TRUE,
      forecast = as.numeric(sigma_forecast),
      conditional_variance = as.numeric(conditional_var),
      long_run_variance = as.numeric(fit@fit$matcoef["omega", 1]),
      model = model_type
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = as.character(e$message)
    )
  })
})

# Forecast using ARIMA model
pr$post("/forecast/arima", function(req) {
  tryCatch({
    data <- fromJSON(req$postBody)
    returns <- data$returns
    horizon <- ifelse(is.null(data$horizon), 7, data$horizon)

    # Fit ARIMA model
    fit <- auto.arima(returns)

    # Forecast
    forecast_result <- forecast(fit, h = horizon)

    list(
      success = TRUE,
      forecast = as.numeric(forecast_result$mean),
      lower_80 = as.numeric(forecast_result$lower[, 2]),
      upper_80 = as.numeric(forecast_result$upper[, 2]),
      lower_95 = as.numeric(forecast_result$lower[, 2]),
      upper_95 = as.numeric(forecast_result$upper[, 2]),
      arima_order = as.vector(arimaorder(fit))
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = as.character(e$message)
    )
  })
})

# Test for cointegration
pr$post("/test/cointegration", function(req) {
  tryCatch({
    data <- fromJSON(req$postBody)
    series1 <- data$series1
    series2 <- data$series2

    # Combine into matrix
    combined <- cbind(series1, series2)

    # Perform cointegration test
    test_result <- po.test(combined)

    list(
      success = TRUE,
      statistic = test_result$statistic,
      p_value = test_result$p.value,
      is_cointegrated = test_result$p.value < 0.05
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = as.character(e$message)
    )
  })
})

# Perform Granger causality test
pr$post("/test/granger", function(req) {
  tryCatch({
    data <- fromJSON(req$postBody)
    x <- data$x
    y <- data$y
    lag <- ifelse(is.null(data$lag), 5, data$lag)

    # Perform Granger causality test
    test_result <- grangertest(x, y, lag)

    list(
      success = TRUE,
      f_statistic = test_result$statistic[1],
      p_value = test_result$p.value[1],
      x_causes_y = test_result$p.value[1] < 0.05
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = as.character(e$message)
    )
  })
})

# Calculate Value at Risk using historical method
pr$post("/risk/var", function(req) {
  tryCatch({
    data <- fromJSON(req$postBody)
    returns <- data$returns
    confidence <- ifelse(is.null(data$confidence), 0.95, data$confidence)
    portfolio_value <- ifelse(is.null(data$portfolio_value), 10000, data$portfolio_value)

    # Calculate VaR
    var_index <- floor((1 - confidence) * length(returns))
    sorted_returns <- sort(returns)
    var <- sorted_returns[var_index]

    # Calculate Expected Shortfall (CVaR)
    cvar <- mean(sorted_returns[1:var_index])

    list(
      success = TRUE,
      var = var * portfolio_value,
      cvar = cvar * portfolio_value,
      var_percentage = var * 100,
      cvar_percentage = cvar * 100
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = as.character(e$message)
    )
  })
})

# Perform quantile regression
pr$post("/regression/quantile", function(req) {
  tryCatch({
    data <- fromJSON(req$postBody)
    x <- data$x
    y <- data$y
    tau <- ifelse(is.null(data$tau), 0.5, data$tau)

    # Fit quantile regression
    fit <- rq(y ~ x, tau = tau)

    list(
      success = TRUE,
      intercept = coef(fit)[1],
      slope = coef(fit)[2],
      tau = tau
    )
  }, error = function(e) {
    list(
      success = FALSE,
      error = as.character(e$message)
    )
  })
})

# Start server
if (!interactive()) {
  pr$run(host = "0.0.0.0", port = 8083)
}
