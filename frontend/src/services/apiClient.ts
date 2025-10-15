import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

// APIクライアントのベースURL
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Axiosインスタンスを作成
const apiClient: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10秒でタイムアウト
});

// リクエストインターセプター: 認証トークンを自動付与
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // localStorageからauthTokenを取得
    const authToken = localStorage.getItem("authToken");

    if (authToken && config.headers) {
      // Authorization: Token {token} ヘッダーを付与
      config.headers.Authorization = `Token ${authToken}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター: エラーハンドリング
apiClient.interceptors.response.use(
  (response) => {
    // 成功レスポンスはそのまま返す
    return response;
  },
  (error: AxiosError) => {
    // 401 Unauthorized の場合
    if (error.response?.status === 401) {
      // localStorageからauthTokenを削除
      localStorage.removeItem("authToken");

      // ログインページへリダイレクト
      // ただし、既にログインページにいる場合はリダイレクトしない
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    // エラーメッセージを統一形式で処理
    type ErrorResponse = { message?: string; detail?: string };
    const errorMessage =
      (error.response?.data as ErrorResponse)?.message ||
      (error.response?.data as ErrorResponse)?.detail ||
      error.message ||
      "An error occurred";

    // エラーオブジェクトを拡張して返す
    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
      originalError: error,
    });
  }
);

export default apiClient;
