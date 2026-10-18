using HTTP
using JSON3
using JuMP
using HiGHS
using LinearAlgebra
using Statistics

"""
Portfolio Optimizer Service
HTTP API for real-time portfolio optimization using convex optimization
"""

# Request/Response structures
struct OptimizeRequest
    assets::Vector{String}
    expected_returns::Vector{Float64}
    covariance_matrix::Vector{Vector{Float64}}
    max_positions::Int
    max_position_weight::Float64
    min_return::Float64
end

struct OptimizeResponse
    success::Bool
    optimal_weights::Vector{Float64}
    expected_return::Float64
    expected_risk::Float64
    sharpe_ratio::Float64
    error::String
end

function parse_request(body::String)
    try
        data = JSON3.read(body)
        return OptimizeRequest(
            data.assets,
            data.expected_returns,
            data.covariance_matrix,
            get(data, :max_positions, 20),
            get(data, :max_position_weight, 0.2),
            get(data, :min_return, 0.0)
        )
    catch e
        @error "Failed to parse request: $e"
        return nothing
    end
end

"""
Optimize portfolio using mean-variance optimization
"""
function optimize_portfolio(req::OptimizeRequest)::OptimizeResponse
    try
        n = length(req.assets)

        # Create optimization model
        model = Model(HiGHS.Optimizer)
        set_silent(model)

        # Decision variables: weights for each asset
        @variable(model, w[1:n] >= 0)

        # Constraint: weights sum to 1
        @constraint(model, sum(w) == 1)

        # Constraint: maximum weight per position
        @constraint(model, [i=1:n], w[i] <= req.max_position_weight)

        # Constraint: minimum expected return
        @constraint(model, sum(req.expected_returns[i] * w[i] for i in 1:n) >= req.min_return)

        # Constraint: maximum number of positions (using binary variables)
        @variable(model, y[1:n], Bin)
        @constraint(model, [i=1:n], w[i] <= y[i])
        @constraint(model, sum(y) <= req.max_positions)

        # Objective: minimize portfolio variance
        Sigma = hcat(req.covariance_matrix...)
        @objective(model, Min, sum(Sigma[i,j] * w[i] * w[j] for i in 1:n, j in 1:n))

        # Solve
        optimize!(model)

        if termination_status(model) != MOI.OPTIMAL
            return OptimizeResponse(false, [], 0.0, 0.0, 0.0, "Optimization failed")
        end

        # Extract results
        weights = value.(w)
        expected_return = sum(req.expected_returns[i] * weights[i] for i in 1:n)
        expected_risk = sqrt(sum(Sigma[i,j] * weights[i] * weights[j] for i in 1:n, j in 1:n))
        sharpe_ratio = expected_return / expected_risk

        return OptimizeResponse(true, weights, expected_return, expected_risk, sharpe_ratio, "")
    catch e
        @error "Optimization error: $e"
        return OptimizeResponse(false, [], 0.0, 0.0, 0.0, string(e))
    end
end

"""
CVaR (Conditional Value at Risk) optimization
"""
function optimize_cvar(req::OptimizeRequest)::OptimizeResponse
    try
        n = length(req.assets)

        # Simplified CVaR optimization
        # In production, this would use historical return scenarios
        model = Model(HiGHS.Optimizer)
        set_silent(model)

        @variable(model, w[1:n] >= 0)
        @variable(model, VaR)
        @variable(model, u[1:100] >= 0)  # 100 scenarios

        @constraint(model, sum(w) == 1)
        @constraint(model, [i=1:n], w[i] <= req.max_position_weight)

        # CVaR constraints (simplified)
        alpha = 0.95  # 95% confidence
        @constraint(model, [s=1:100], u[s] >= VaR - sum(req.expected_returns[i] * w[i] for i in 1:n))
        @constraint(model, VaR + (1/((1-alpha)*100)) * sum(u[s] for s in 1:100) <= 0.1)

        @objective(model, Min, VaR + (1/((1-alpha)*100)) * sum(u[s] for s in 1:100))

        optimize!(model)

        if termination_status(model) != MOI.OPTIMAL
            return OptimizeResponse(false, [], 0.0, 0.0, 0.0, "CVaR optimization failed")
        end

        weights = value.(w)
        expected_return = sum(req.expected_returns[i] * weights[i] for i in 1:n)
        expected_risk = sqrt(sum(req.covariance_matrix[i][j] * weights[i] * weights[j] for i in 1:n, j in 1:n))

        return OptimizeResponse(true, weights, expected_return, expected_risk, 0.0, "")
    catch e
        @error "CVaR optimization error: $e"
        return OptimizeResponse(false, [], 0.0, 0.0, 0.0, string(e))
    end
end

"""
HTTP handler for /optimize endpoint
"""
function handle_optimize(req::HTTP.Request)
    body = String(req.body)
    parsed = parse_request(body)

    if parsed === nothing
        return HTTP.Response(400, "Invalid request")
    end

    response = optimize_portfolio(parsed)

    return HTTP.Response(200, JSON3.write(Dict(
        "success" => response.success,
        "optimal_weights" => response.optimal_weights,
        "expected_return" => response.expected_return,
        "expected_risk" => response.expected_risk,
        "sharpe_ratio" => response.sharpe_ratio,
        "error" => response.error
    )))
end

"""
HTTP handler for /optimize/cvar endpoint
"""
function handle_optimize_cvar(req::HTTP.Request)
    body = String(req.body)
    parsed = parse_request(body)

    if parsed === nothing
        return HTTP.Response(400, "Invalid request")
    end

    response = optimize_cvar(parsed)

    return HTTP.Response(200, JSON3.write(Dict(
        "success" => response.success,
        "optimal_weights" => response.optimal_weights,
        "expected_return" => response.expected_return,
        "expected_risk" => response.expected_risk,
        "error" => response.error
    )))
end

"""
Start HTTP server
"""
function start_server(port::Int=8081)
    println("Julia Portfolio Optimizer started on port $port")

    HTTP.serve() do request::HTTP.Request
        path = request.target
        body = String(request.body)

        if request.method == "POST" && path == "/optimize"
            parsed = parse_request(body)
            if parsed === nothing
                return HTTP.Response(400, "Invalid request")
            end
            response = optimize_portfolio(parsed)
            return HTTP.Response(200, JSON3.write(Dict(
                "success" => response.success,
                "optimal_weights" => response.optimal_weights,
                "expected_return" => response.expected_return,
                "expected_risk" => response.expected_risk,
                "sharpe_ratio" => response.sharpe_ratio,
                "error" => response.error
            )))
        elseif request.method == "POST" && path == "/optimize/cvar"
            parsed = parse_request(body)
            if parsed === nothing
                return HTTP.Response(400, "Invalid request")
            end
            response = optimize_cvar(parsed)
            return HTTP.Response(200, JSON3.write(Dict(
                "success" => response.success,
                "optimal_weights" => response.optimal_weights,
                "expected_return" => response.expected_return,
                "expected_risk" => response.expected_risk,
                "error" => response.error
            )))
        else
            return HTTP.Response(404, "Not found")
        end
    end
end

# Start server if run directly
if abspath(PROGRAM_FILE) == @__FILE__
    start_server(8081)
end
