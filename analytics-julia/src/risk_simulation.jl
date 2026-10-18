using HTTP
using JSON3
using Random
using Statistics
using Distributions

"""
Risk Simulation Engine
Monte Carlo simulation for portfolio VaR and scenario analysis
"""

struct RiskSimulationRequest
    portfolio_value::Float64
    assets::Vector{String}
    weights::Vector{Float64}
    returns::Vector{Vector{Float64}}  # Historical returns for each asset
    confidence_level::Float64
    time_horizon_days::Int
    num_simulations::Int
end

struct RiskSimulationResponse
    success::Bool
    var::Float64
    cvar::Float64
    expected_return::Float64
    worst_case_return::Float64
    best_case_return::Float64
    error::String
end

function parse_risk_request(body::String)
    try
        data = JSON3.read(body)
        return RiskSimulationRequest(
            data.portfolio_value,
            data.assets,
            data.weights,
            data.returns,
            get(data, :confidence_level, 0.95),
            get(data, :time_horizon_days, 30),
            get(data, :num_simulations, 10000)
        )
    catch e
        @error "Failed to parse risk request: $e"
        return nothing
    end
end

"""
Monte Carlo simulation for portfolio VaR
"""
function monte_carlo_var(req::RiskSimulationRequest)::RiskSimulationResponse
    try
        n_assets = length(req.assets)
        n_days = req.time_horizon_days
        n_sims = req.num_simulations

        # Calculate mean returns and covariance matrix
        mean_returns = [mean(req.returns[i]) for i in 1:n_assets]
        cov_matrix = cov(hcat(req.returns...))

        # Cholesky decomposition for correlated random numbers
        L = cholesky(cov_matrix).L

        # Simulate portfolio returns
        portfolio_returns = Float64[]

        for sim in 1:n_sims
            # Generate correlated random shocks
            z = rand(MvNormal(zeros(n_assets), I))
            correlated_shocks = L * z

            # Calculate daily returns
            daily_returns = mean_returns .+ correlated_shocks

            # Calculate portfolio return over time horizon
            portfolio_return = sum(req.weights[i] * daily_returns[i] for i in 1:n_assets) * n_days
            push!(portfolio_returns, portfolio_return)
        end

        # Sort returns
        sorted_returns = sort(portfolio_returns)

        # Calculate VaR
        var_index = Int(floor((1 - req.confidence_level) * n_sims))
        var = sorted_returns[var_index]

        # Calculate CVaR (Expected Shortfall)
        cvar = mean(sorted_returns[1:var_index])

        # Calculate statistics
        expected_return = mean(portfolio_returns)
        worst_case = minimum(portfolio_returns)
        best_case = maximum(portfolio_returns)

        return RiskSimulationResponse(
            true,
            var * req.portfolio_value,
            cvar * req.portfolio_value,
            expected_return * req.portfolio_value,
            worst_case * req.portfolio_value,
            best_case * req.portfolio_value,
            ""
        )
    catch e
        @error "Monte Carlo simulation error: $e"
        return RiskSimulationResponse(false, 0, 0, 0, 0, 0, string(e))
    end
end

"""
Geometric Brownian Motion simulation
"""
function gbm_simulation(req::RiskSimulationRequest)::RiskSimulationResponse
    try
        n_assets = length(req.assets)
        n_days = req.time_horizon_days
        n_sims = req.num_simulations

        # Calculate drift and volatility
        mean_returns = [mean(req.returns[i]) for i in 1:n_assets]
        volatilities = [std(req.returns[i]) for i in 1:n_assets]

        # Simulate GBM paths
        portfolio_values = Float64[]

        for sim in 1:n_sims
            portfolio_value = req.portfolio_value

            for day in 1:n_days
                for i in 1:n_assets
                    # GBM: dS = mu*S*dt + sigma*S*dW
                    dt = 1/252  # Trading days
                    dW = rand(Normal(0, sqrt(dt)))
                    asset_return = mean_returns[i] * dt + volatilities[i] * dW

                    # Update portfolio value
                    portfolio_value += portfolio_value * req.weights[i] * asset_return
                end
            end

            push!(portfolio_values, portfolio_value)
        end

        # Calculate P&L
        pnl = portfolio_values .- req.portfolio_value
        sorted_pnl = sort(pnl)

        # VaR and CVaR
        var_index = Int(floor((1 - req.confidence_level) * n_sims))
        var = sorted_pnl[var_index]
        cvar = mean(sorted_pnl[1:var_index])

        return RiskSimulationResponse(
            true,
            var,
            cvar,
            mean(pnl),
            minimum(pnl),
            maximum(pnl),
            ""
        )
    catch e
        @error "GBM simulation error: $e"
        return RiskSimulationResponse(false, 0, 0, 0, 0, 0, string(e))
    end
end

"""
HTTP handler for /risk/var endpoint
"""
function handle_var(req::HTTP.Request)
    body = String(req.body)
    parsed = parse_risk_request(body)

    if parsed === nothing
        return HTTP.Response(400, "Invalid request")
    end

    response = monte_carlo_var(parsed)

    return HTTP.Response(200, JSON3.write(Dict(
        "success" => response.success,
        "var" => response.var,
        "cvar" => response.cvar,
        "expected_return" => response.expected_return,
        "worst_case" => response.worst_case_return,
        "best_case" => response.best_case_return,
        "error" => response.error
    )))
end

"""
HTTP handler for /risk/gbm endpoint
"""
function handle_gbm(req::HTTP.Request)
    body = String(req.body)
    parsed = parse_risk_request(body)

    if parsed === nothing
        return HTTP.Response(400, "Invalid request")
    end

    response = gbm_simulation(parsed)

    return HTTP.Response(200, JSON3.write(Dict(
        "success" => response.success,
        "var" => response.var,
        "cvar" => response.cvar,
        "expected_return" => response.expected_return,
        "worst_case" => response.worst_case_return,
        "best_case" => response.best_case_return,
        "error" => response.error
    )))
end

"""
Start HTTP server
"""
function start_server(port::Int=8082)
    println("Julia Risk Simulation Engine started on port $port")

    HTTP.serve() do request::HTTP.Request
        path = request.target
        if request.method == "POST" && path == "/risk/var"
            return handle_var(request)
        elseif request.method == "POST" && path == "/risk/gbm"
            return handle_gbm(request)
        else
            return HTTP.Response(404, "Not found")
        end
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    start_server(8082)
end
