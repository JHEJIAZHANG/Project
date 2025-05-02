import SwiftUI
import PhotosUI // Import PhotosUI for PhotosPicker

struct EditProfileView: View {
    @EnvironmentObject var authManager: AuthManager
    @Environment(\.presentationMode) var presentationMode
    
    // --- State for editable fields ---
    @State private var username: String = ""
    @State private var department: String = "" // Placeholder for department/class
    
    // --- State for Image Picker ---
    @State private var selectedPhotoItem: PhotosPickerItem? // Holds the selected item from the picker
    @State private var avatarData: Data? // Holds the actual image data
    @State private var avatarImage: Image? // Holds the Image view to display
    
    // --- Non-editable fields (example) ---
    private var email: String {
        authManager.currentUser?.email ?? "未知 Email"
    }
    
    var body: some View {
        Form {
            // --- Avatar Section ---
            Section {
                HStack {
                    Spacer()
                    VStack {
                        // Display selected image or placeholder
                        ZStack {
                             // Show placeholder if avatarImage is nil
                             if avatarImage == nil {
                                 Image(systemName: "person.circle.fill") // TODO: Load initial user image if available
                                     .resizable()
                                     .scaledToFit()
                                     .frame(width: 100, height: 100)
                                     .clipShape(Circle())
                                     .foregroundColor(.gray)
                             }
                            // Show the selected image
                             avatarImage?
                                .resizable()
                                .scaledToFill() // Use scaledToFill to cover the circle
                                .frame(width: 100, height: 100)
                                .clipShape(Circle())
                         }
                        
                        // Use PhotosPicker to wrap the button
                        PhotosPicker(selection: $selectedPhotoItem, matching: .images, photoLibrary: .shared()) {
                             Text("更改頭像")
                        }
                        .padding(.top, 5)
                        // Placeholder Text after commenting out - REMOVED
                    }
                    Spacer()
                }
            }
            .listRowBackground(Color.clear) // Make background transparent
            
            // --- Basic Info Section ---
            Section("基本資料") {
                HStack {
                     Text("使用者名稱")
                    Spacer()
                     TextField("請輸入名稱", text: $username)
                         .multilineTextAlignment(.trailing)
                 }
                HStack {
                    Text("Email")
                    Spacer()
                    Text(email)
                        .foregroundColor(.gray) // Non-editable appearance
                }
                HStack {
                    Text("系級")
                    Spacer()
                    TextField("例如：資工四", text: $department)
                         .multilineTextAlignment(.trailing)
                }
                // Add other fields as needed (e.g., student ID if available)
            }
        }
        .navigationTitle("編輯個人資料")
        .navigationBarTitleDisplayMode(.inline)
        .navigationBarBackButtonHidden(true) // Use custom buttons
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button("取消") {
                    presentationMode.wrappedValue.dismiss()
                }
            }
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("儲存") {
                    saveProfile()
                }
                .disabled(username.isEmpty || department.isEmpty) // Basic validation
            }
        }
        .onAppear {
            // Load current user data into @State variables when view appears
            if let user = authManager.currentUser {
                self.username = user.username
                self.department = "資訊工程學系 四年級" // Using placeholder from ProfileView for now
                // TODO: Load existing avatar data/image if available from user.profileImageURL or similar
            } else {
                self.username = ""
                self.department = ""
            }
        }
        // Add onChange modifier to handle photo selection
//        .onChange(of: selectedPhotoItem) { newItem in
//             Task {
//                 // Retrieve selected asset in the form of Data
//                 if let data = try? await newItem?.loadTransferable(type: Data.self) {
//                     avatarData = data
//                     if let uiImage = UIImage(data: data) {
//                         avatarImage = Image(uiImage: uiImage)
//                     }
//                 }
//             }
//         }
    }
    
    private func saveProfile() {
        print("Saving profile...")
        // TODO: Update the AuthManager or call an API, including avatarData if it changed
        if authManager.currentUser != nil {
            authManager.currentUser?.username = username
            print("Profile updated locally (Username: \(username), Department: \(department))") // Log changes
//             if let data = avatarData {
//                 print("Avatar data is available (\(data.count) bytes), ready to upload.")
//                 // TODO: Add API call to upload avatarData
//                 // TODO: Update authManager.currentUser.profileImageURL after successful upload
//             }
        }
        
        // Simulate saving and dismiss
        presentationMode.wrappedValue.dismiss()
    }
}

// MARK: - Preview
#if DEBUG
struct EditProfileView_Previews: PreviewProvider {
    static var previews: some View {
        // Wrap in NavigationView for preview context
        NavigationView {
            EditProfileView()
                .environmentObject(AuthManager.mock) // Use a mock AuthManager
        }
    }
}

// Create a mock AuthManager for preview
extension AuthManager {
    static var mock: AuthManager {
        let manager = AuthManager()
        manager.currentUser = User(username: "PreviewUser", email: "preview@ntub.edu.tw", profileImageURL: nil)
        manager.isLoggedIn = true
        return manager
    }
}
#endif 