import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { Asset, Portfolio } from "../services/api";
import { addMoney, buyAsset, getPortfolio, sellAsset } from "../services/api";

const Dashboard = () => {
  const navigate = useNavigate();
  const { logout: authLogout } = useAuth();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Transaction states
  const [buySymbol, setBuySymbol] = useState("");
  const [buyQuantity, setBuyQuantity] = useState("");
  const [sellSymbol, setSellSymbol] = useState("");
  const [sellQuantity, setSellQuantity] = useState("");
  const [addMoneyAmount, setAddMoneyAmount] = useState("");

  // Modal states
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [showSellModal, setShowSellModal] = useState(false);
  const [showAddMoneyModal, setShowAddMoneyModal] = useState(false);
  const [transactionLoading, setTransactionLoading] = useState(false);

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      const response = await getPortfolio();
      setPortfolio(response.data);
      setError("");
    } catch (err: any) {
      setError("Failed to load portfolio data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!buySymbol || !buyQuantity) return;

    try {
      setTransactionLoading(true);
      await buyAsset(buySymbol.toUpperCase(), Number(buyQuantity));
      await fetchPortfolio();
      setShowBuyModal(false);
      setBuySymbol("");
      setBuyQuantity("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to buy asset");
    } finally {
      setTransactionLoading(false);
    }
  };

  const handleSell = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sellSymbol || !sellQuantity) return;

    try {
      setTransactionLoading(true);
      await sellAsset(sellSymbol.toUpperCase(), Number(sellQuantity));
      await fetchPortfolio();
      setShowSellModal(false);
      setSellSymbol("");
      setSellQuantity("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to sell asset");
    } finally {
      setTransactionLoading(false);
    }
  };

  const handleAddMoney = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!addMoneyAmount) return;

    try {
      setTransactionLoading(true);
      await addMoney(Number(addMoneyAmount));
      await fetchPortfolio();
      setShowAddMoneyModal(false);
      setAddMoneyAmount("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add money");
    } finally {
      setTransactionLoading(false);
    }
  };

  const handleLogout = () => {
    authLogout();
    navigate("/login");
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-blue-500 to-purple-500">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-blue-500 to-purple-500">
      <div className="backdrop-blur-md bg-white/70 shadow-2xl rounded-2xl p-6 sm:p-10 max-w-4xl w-full">
        {/* Header */}
        <header className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 text-center sm:text-left mb-4 sm:mb-0">
            Trading Dashboard
          </h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-base font-semibold rounded-lg text-white bg-gradient-to-r from-red-500 to-pink-500 shadow-lg hover:from-red-600 hover:to-pink-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-400 transition"
          >
            Logout
          </button>
        </header>

        {/* Main Content */}
        <main>
          {error && (
            <div className="mb-4 rounded-md bg-red-100 p-3">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          {portfolio && (
            <>
              {/* Portfolio Overview */}
              <div className="bg-white/80 backdrop-blur rounded-lg shadow p-6 mb-6">
                <h2 className="text-xl font-semibold mb-4 text-black">Portfolio Overview</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-4 bg-gray-50/80 rounded-lg">
                    <p className="text-sm text-black">Total Value</p>
                    <p className="text-2xl font-bold text-black">
                      {formatCurrency(portfolio.total_value)}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50/80 rounded-lg">
                    <p className="text-sm text-black">Available Cash</p>
                    <p className="text-2xl font-bold text-black">
                      {formatCurrency(portfolio.available_money)}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50/80 rounded-lg">
                    <p className="text-sm text-black">Total Added</p>
                    <p className="text-2xl font-bold text-black">
                      {formatCurrency(portfolio.total_added_money)}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50/80 rounded-lg">
                    <p className="text-sm text-black">Performance</p>
                    <p
                      className={
                        portfolio.performance_abs >= 0
                          ? "text-2xl font-bold text-green-600"
                          : "text-2xl font-bold text-red-600"
                      }
                    >
                      {formatCurrency(portfolio.performance_abs)} (
                      {formatPercentage(portfolio.performance_rel)})
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-4 mb-6">
                <button
                  onClick={() => setShowBuyModal(true)}
                  className="px-4 py-2 text-base font-semibold rounded-lg text-white bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg hover:from-indigo-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-400 transition"
                >
                  Buy Asset
                </button>
                <button
                  onClick={() => setShowSellModal(true)}
                  className="px-4 py-2 text-base font-semibold rounded-lg text-white bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg hover:from-indigo-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-400 transition"
                >
                  Sell Asset
                </button>
                <button
                  onClick={() => setShowAddMoneyModal(true)}
                  className="px-4 py-2 text-base font-semibold rounded-lg text-white bg-gradient-to-r from-green-500 to-emerald-500 shadow-lg hover:from-green-600 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-400 transition"
                >
                  Add Money
                </button>
              </div>

              {/* Assets Table */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <h2 className="text-xl font-semibold p-6 pb-0">Your Assets</h2>
                {portfolio.assets.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">
                    You don't have any assets yet. Start buying some!
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
                          >
                            Symbol
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
                          >
                            Quantity
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
                          >
                            Current Price
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
                          >
                            Total Value
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
                          >
                            Performance ($)
                          </th>
                          <th
                            scope="col"
                            className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"
                          >
                            Performance (%)
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {portfolio.assets.map((asset: Asset) => (
                          <tr key={asset.symbol}>
                            <td className="px-6 py-4 whitespace-nowrap font-medium text-black">
                              {asset.symbol}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-black">
                              {asset.quantity}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-black">
                              {formatCurrency(asset.current_price)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-black">
                              {formatCurrency(asset.total_value)}
                            </td>
                            <td
                              className={
                                asset.performance_abs >= 0
                                  ? "px-6 py-4 whitespace-nowrap text-green-600"
                                  : "px-6 py-4 whitespace-nowrap text-red-600"
                              }
                            >
                              {formatCurrency(asset.performance_abs)}
                            </td>
                            <td
                              className={
                                asset.performance_rel >= 0
                                  ? "px-6 py-4 whitespace-nowrap text-green-600"
                                  : "px-6 py-4 whitespace-nowrap text-red-600"
                              }
                            >
                              {formatPercentage(asset.performance_rel)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </main>
      </div>

      {/* Buy Modal */}
      {showBuyModal && (
        <div className="fixed inset-0 flex items-center justify-center p-4 z-50" style={{background: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 50%, #a21caf 100%)', backgroundBlendMode: 'multiply'}}>
          <div className="backdrop-blur-md bg-white/70 shadow-2xl rounded-2xl p-8 max-w-md w-full">
            <h3 className="text-lg font-bold text-black mb-4 text-center">Buy Asset</h3>
            <form onSubmit={handleBuy}>
              <div className="mb-4">
                <label htmlFor="buySymbol" className="block text-sm font-medium text-black">Symbol</label>
                <input type="text" id="buySymbol" value={buySymbol} onChange={(e) => setBuySymbol(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black placeholder-black bg-white" placeholder="e.g. AAPL" required />
              </div>
              <div className="mb-4">
                <label htmlFor="buyQuantity" className="block text-sm font-medium text-black">Quantity</label>
                <input type="number" id="buyQuantity" value={buyQuantity} onChange={(e) => setBuyQuantity(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black placeholder-black bg-white" min="0.01" step="0.01" placeholder="0.00" required />
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button type="button" onClick={() => setShowBuyModal(false)} className="px-4 py-2 border border-gray-400 rounded-lg text-sm font-medium text-white bg-gray-500 shadow hover:bg-gray-700 transition">Cancel</button>
                <button type="submit" disabled={transactionLoading} className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg hover:from-indigo-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-400 disabled:opacity-60 transition">{transactionLoading ? "Processing..." : "Buy"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Sell Modal */}
      {showSellModal && (
        <div className="fixed inset-0 flex items-center justify-center p-4 z-50" style={{background: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 50%, #a21caf 100%)', backgroundBlendMode: 'multiply'}}>
          <div className="backdrop-blur-md bg-white/70 shadow-2xl rounded-2xl p-8 max-w-md w-full">
            <h3 className="text-lg font-bold text-black mb-4 text-center">Sell Asset</h3>
            <form onSubmit={handleSell}>
              <div className="mb-4">
                <label htmlFor="sellSymbol" className="block text-sm font-medium text-black">Symbol</label>
                <input type="text" id="sellSymbol" value={sellSymbol} onChange={(e) => setSellSymbol(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black placeholder-black bg-white" placeholder="e.g. AAPL" required />
              </div>
              <div className="mb-4">
                <label htmlFor="sellQuantity" className="block text-sm font-medium text-black">Quantity</label>
                <input type="number" id="sellQuantity" value={sellQuantity} onChange={(e) => setSellQuantity(e.target.value)} className="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black placeholder-black bg-white" min="0.01" step="0.01" placeholder="0.00" required />
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button type="button" onClick={() => setShowSellModal(false)} className="px-4 py-2 border border-gray-400 rounded-lg text-sm font-medium text-white bg-gray-500 shadow hover:bg-gray-700 transition">Cancel</button>
                <button type="submit" disabled={transactionLoading} className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg hover:from-indigo-600 hover:to-purple-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-400 disabled:opacity-60 transition">{transactionLoading ? "Processing..." : "Sell"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Money Modal */}
      {showAddMoneyModal && (
        <div className="fixed inset-0 flex items-center justify-center p-4 z-50" style={{background: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 50%, #a21caf 100%)', backgroundBlendMode: 'multiply'}}>
          <div className="backdrop-blur-md bg-white/70 shadow-2xl rounded-2xl p-8 max-w-md w-full">
            <h3 className="text-lg font-bold text-black mb-4 text-center">Add Money</h3>
            <form onSubmit={handleAddMoney}>
              <div className="mb-4">
                <label htmlFor="addMoneyAmount" className="block text-sm font-medium text-black">Amount</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="text-black sm:text-sm">$</span>
                  </div>
                  <input type="number" id="addMoneyAmount" value={addMoneyAmount} onChange={(e) => setAddMoneyAmount(e.target.value)} className="block w-full pl-7 pr-12 border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-black placeholder-black bg-white" placeholder="0.00" min="1" step="1" required />
                </div>
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button type="button" onClick={() => setShowAddMoneyModal(false)} className="px-4 py-2 border border-gray-400 rounded-lg text-sm font-medium text-white bg-gray-500 shadow hover:bg-gray-700 transition">Cancel</button>
                <button type="submit" disabled={transactionLoading} className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-green-500 to-emerald-500 shadow-lg hover:from-green-600 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-400 disabled:opacity-60 transition">{transactionLoading ? "Processing..." : "Add Money"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
