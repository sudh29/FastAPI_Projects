import axios from "axios";

const API_URL = "http://localhost:8000";

let accessToken: string | null = localStorage.getItem("access_token");

export function setAccessToken(token: string) {
  accessToken = token;
  localStorage.setItem("access_token", token);
}

export function clearAccessToken() {
  accessToken = null;
  localStorage.removeItem("access_token");
}


function getAuthHeaders() {
  return accessToken
    ? { Authorization: `Bearer ${accessToken}` }
    : {};
}

// Register a new user
export async function register(username: string, password: string) {
  const response = await axios.post(`${API_URL}/register`, {
    username,
    password,
  });
  return response.data;
}

// Login and store token
export async function login(username: string, password: string) {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);

  const response = await axios.post(`${API_URL}/login`, params, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  setAccessToken(response.data.access_token);
  return response.data;
}

// Add money to portfolio
export async function addMoney(amount: number) {
  const response = await axios.post(
    `${API_URL}/add-money`,
    { amount },
    { headers: getAuthHeaders() }
  );
  return response.data;
}

// Buy asset
export async function buyAsset(symbol: string, quantity: number) {
  const response = await axios.post(
    `${API_URL}/buy`,
    { symbol, quantity },
    { headers: getAuthHeaders() }
  );
  return response.data;
}

// Sell asset
export async function sellAsset(symbol: string, quantity: number) {
  const response = await axios.post(
    `${API_URL}/sell`,
    { symbol, quantity },
    { headers: getAuthHeaders() }
  );
  return response.data;
}

// Get portfolio
export async function getPortfolio() {
  const response = await axios.get(`${API_URL}/portfolio`, {
    headers: getAuthHeaders(),
  });
  return response.data;
}
