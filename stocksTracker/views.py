from django.contrib import messages
from django.shortcuts import redirect, render,HttpResponse

from stocksTracker.forms import PortfolioForm
from .tracker_scripts import calculate_performance, fetch_historical_data_from_file, fetch_historical_data_in_file, fetch_historical_data_in_file_all, fetch_real_time_data, fetch_real_time_data_all, fetch_realtime_data_from_file, run_simulator,trade_analyzer

def index(request):
    return render(request, 'index.html')

def testing(request):
    return HttpResponse()


def portfolio_summary_view(request):
    current_value, initial_value, portfolio_gain_loss, gains = calculate_performance()
    context = {
        "initial_value": initial_value,
        "current_value": current_value,
        "portfolio_gain_loss": portfolio_gain_loss,
        "gains": gains
    }
    return render(request, 'stocksTracker/portfolio_summary.html', context)


def stock_signals_view(request):
    stocks = ["AAPL", "GOOGL", "MSFT"]
    signals = trade_analyzer(stocks)
    context = {"signals": signals}
    return render(request, 'stocksTracker/stock_signals.html', context)


def data_collection_view(request):
    if request.method == "POST":
        real_time_data = fetch_real_time_data_all()
        
        fetch_historical_data_in_file_all()
        
        context = {
            "real_time_data": real_time_data,
        }
        return render(request, 'stocksTracker/data_collection.html', context)
    else:
        return render(request, 'stocksTracker/data_collection.html')


PORTFOLIO = {}


def portfolio_view(request):
    global PORTFOLIO

    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            # Process form data
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            stocks_input = form.cleaned_data["stocks"]

            try:
                stocks_list = []
                for stock_entry in stocks_input.split(","):
                    symbol, shares = stock_entry.strip().split(":")
                    stocks_list.append({"stock": symbol.strip(), "shares": int(shares.strip())})
                
                PORTFOLIO["name"] = name
                PORTFOLIO["email"] = email
                PORTFOLIO["phone"] = phone
                PORTFOLIO["stocks"] = stocks_list

            except ValueError:
                form.add_error(None, "Invalid stock input format. Please use the correct format.")
                return render(request, 'stocksTracker/portfolio.html', {"form": form})

            return redirect("portfolio_details")
    else:
        form = PortfolioForm()

    return render(request, 'stocksTracker/portfolio.html', {"form": form})




def portfolio_details_view(request):
    global PORTFOLIO

    context = {"portfolio": PORTFOLIO}
    return render(request, 'stocksTracker/portfolio_details.html', context)


def calculate_portfolio_value_view(request):
    global PORTFOLIO

    try:
        total_value = 0
        for item in PORTFOLIO.get("stocks", []):
            price, _ = fetch_realtime_data_from_file(item["stock"])
            if price is None:
                continue
            total_value += price * item["shares"]

        return render(request, 'stocksTracker/portfolio_value.html', {"total_value": total_value})
    except Exception as e:
        return render(request, 'stocksTracker/portfolio_value.html', {"error": str(e)})


def calculate_performance_view(request):
    global PORTFOLIO

    try:
        current_value = 0
        initial_value = 0
        gains = {}

        for item in PORTFOLIO.get("stocks", []):
            symbol = item["stock"]
            shares = item["shares"]

            initial_price, _ = fetch_historical_data_from_file(symbol)
            price, _ = fetch_realtime_data_from_file(symbol)

            if initial_price is None or price is None:
                continue

            initial_value += initial_price * shares
            current_value += price * shares

            gains[symbol] = ((price - initial_price) / initial_price) * 100

        portfolio_gain_loss = ((current_value - initial_value) / initial_value) * 100

        context = {
            "current_value": current_value,
            "initial_value": initial_value,
            "portfolio_gain_loss": portfolio_gain_loss,
            "gains": gains
        }
        return render(request, 'stocksTracker/portfolio_performance.html', context)
    except Exception as e:
        return render(request, 'stocksTracker/portfolio_performance.html', {"error": str(e)})



# Trade Analyzer View
def trade_analyzer_view(request):
    stocks_list = ["AAPL", "GOOG", "MSFT"]  # Example stock symbols
    trade_signals = trade_analyzer(stocks_list)

    # Format the trade signals for display
    formatted_signals = {}
    for signal in trade_signals:
        stock = signal["stock"]
        signal_text = f"- {signal['signal']} on {signal['date'].strftime('%b. %d, %Y, midnight')}"
        if stock not in formatted_signals:
            formatted_signals[stock] = []
        formatted_signals[stock].append(signal_text)

    return render(request, "stocksTracker/trade_analyzer.html", {"signals": formatted_signals})




def run_simulation_view(request):
    if not PORTFOLIO or not PORTFOLIO.get("stocks", []):
        messages.error(request, "Your portfolio is not recorded. Please create your portfolio first.")
        return redirect('portfolio_form')

    # Run the simulation
    total_capital, total_portfolio_value, full_trade_history = run_simulator()

    # Render the simulation results
    return render(request, "stocksTracker/simulation_results.html", {
        "total_capital": total_capital,
        "total_portfolio_value": total_portfolio_value,
        "full_trade_history": full_trade_history,
    })