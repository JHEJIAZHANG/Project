import Foundation
import SwiftUI

class LoginViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var isLoggedIn = false
    
    private let baseURL = "http://localhost:8000/api" // 請改為您的實際後端 URL
    
    // 一般登入
    func login(email: String, password: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let url = URL(string: "\(baseURL)/login/")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let body = ["identifier": email, "password": password]
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            if httpResponse.statusCode == 200 {
                let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
                // 儲存 token
                UserDefaults.standard.set(loginResponse.access, forKey: "accessToken")
                UserDefaults.standard.set(loginResponse.refresh, forKey: "refreshToken")
                
                DispatchQueue.main.async {
                    self.isLoggedIn = true
                    self.isLoading = false
                }
            } else {
                let errorResponse = try JSONDecoder().decode(ErrorResponse.self, from: data)
                throw NetworkError.serverError(errorResponse.detail)
            }
        } catch {
            DispatchQueue.main.async {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
    
    // Google 登入
    func googleLogin(accessToken: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let url = URL(string: "\(baseURL)/social-login/")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let body = ["provider": "google", "access_token": accessToken]
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            if httpResponse.statusCode == 200 {
                let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
                UserDefaults.standard.set(loginResponse.access, forKey: "accessToken")
                UserDefaults.standard.set(loginResponse.refresh, forKey: "refreshToken")
                
                DispatchQueue.main.async {
                    self.isLoggedIn = true
                    self.isLoading = false
                }
            } else {
                let errorResponse = try JSONDecoder().decode(ErrorResponse.self, from: data)
                throw NetworkError.serverError(errorResponse.detail)
            }
        } catch {
            DispatchQueue.main.async {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
    
    // LINE 登入
    func lineLogin(code: String, redirectUri: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let url = URL(string: "\(baseURL)/social-login/")!
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let body = [
                "provider": "line",
                "code": code,
                "redirect_uri": redirectUri
            ]
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            if httpResponse.statusCode == 200 {
                let loginResponse = try JSONDecoder().decode(LoginResponse.self, from: data)
                UserDefaults.standard.set(loginResponse.access, forKey: "accessToken")
                UserDefaults.standard.set(loginResponse.refresh, forKey: "refreshToken")
                
                DispatchQueue.main.async {
                    self.isLoggedIn = true
                    self.isLoading = false
                }
            } else {
                let errorResponse = try JSONDecoder().decode(ErrorResponse.self, from: data)
                throw NetworkError.serverError(errorResponse.detail)
            }
        } catch {
            DispatchQueue.main.async {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
}

// 回應模型
struct LoginResponse: Codable {
    let access: String
    let refresh: String
}

struct ErrorResponse: Codable {
    let detail: String
}

// 錯誤類型
enum NetworkError: Error {
    case invalidResponse
    case serverError(String)
} 