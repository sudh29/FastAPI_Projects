import React from "react";

const Dashboard: React.FC = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-100 to-purple-200">
      <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md text-center">
        <h2 className="text-2xl font-bold mb-6 text-purple-700">Dashboard</h2>
        <p className="mb-4">Welcome to your portfolio dashboard!</p>
        <p className="text-gray-600">Portfolio data and actions will appear here.</p>
      </div>
    </div>
  );
};

export default Dashboard;
