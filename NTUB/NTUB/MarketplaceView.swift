import SwiftUI

// MARK: - Data Models for Marketplace
struct MarketplaceItem: Identifiable {
    let id = UUID()
    let name: String
    let price: Int
    let description: String
    let condition: String // e.g., "9成新，無筆記"
    let category: ItemCategory
    let imageName: String? // Use optional String for image name/URL for now
    let sellerName: String
    let sellerDepartment: String // e.g., "資管系 大三"
    let postDate: Date
    let tradeLocation: String
}

enum ItemCategory: String, CaseIterable, Identifiable {
    case all = "全部"
    case textbook = "教科書"
    case stationery = "文具用品"
    case electronics = "3C產品"
    case others = "其他物品"
    var id: String { self.rawValue }
}

// MARK: - Main Marketplace View (Entry Point)
struct MarketplaceView: View {
    var body: some View {
        // The main view will likely host the list and handle navigation
        MarketplaceListView()
    }
}

// MARK: - Marketplace List View
struct MarketplaceListView: View {
    @State private var searchText: String = ""
    @State private var selectedCategory: ItemCategory = .all
    @State private var showingAddItemSheet = false
    
    // --- Mock Data ---
    @State private var items: [MarketplaceItem] = [
        MarketplaceItem(name: "資料庫系統概論 第五版", price: 350, description: "課程用過一學期，保存良好，無筆記和劃線。", condition: "9成新，無筆記", category: .textbook, imageName: "book.closed.fill", sellerName: "林同學", sellerDepartment: "資管系 大三", postDate: Date().addingTimeInterval(-86400*2), tradeLocation: "學校圖書館一樓"),
        MarketplaceItem(name: "MacBook Air 保護套", price: 200, description: "多買的，全新未拆封。", condition: "全新未拆封", category: .electronics, imageName: "laptopcomputer.and.arrow.down", sellerName: "陳同學", sellerDepartment: "企管系 大二", postDate: Date().addingTimeInterval(-86400*1), tradeLocation: "學校星巴克"),
        MarketplaceItem(name: "計算機概論 2023版", price: 400, description: "有做一些重點筆記，不介意者再來。", condition: "8成新，有重點筆記", category: .textbook, imageName: "book.closed.fill", sellerName: "王同學", sellerDepartment: "財金系 大一", postDate: Date().addingTimeInterval(-86400*3), tradeLocation: "承曦樓門口"),
        MarketplaceItem(name: "Apple Pencil 第一代", price: 2500, description: "很少用，附贈一個筆套。", condition: "9成新，附贈筆套", category: .electronics, imageName: "applepencil", sellerName: "李同學", sellerDepartment: "應外系 大四", postDate: Date().addingTimeInterval(-86400*5), tradeLocation: "六藝樓自習室")
    ]
    
    // Filtered items based on search and category
    var filteredItems: [MarketplaceItem] {
        items.filter { item in
            let categoryMatch = (selectedCategory == .all || item.category == selectedCategory)
            let searchMatch = searchText.isEmpty || item.name.localizedCaseInsensitiveContains(searchText)
            return categoryMatch && searchMatch
        }
    }
    
    // Define grid layout
    let columns: [GridItem] = [
        GridItem(.flexible(), spacing: 15),
        GridItem(.flexible(), spacing: 15)
    ]

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 1. Search Bar
                HStack {
                    TextField("搜尋二手物品...", text: $searchText)
                        .padding(10)
                        .padding(.leading, 30)
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .overlay(
                            HStack {
                                Image(systemName: "magnifyingglass")
                                    .foregroundColor(.gray)
                                    .padding(.leading, 8)
                                Spacer()
                            }
                        )
                }
                .padding(.horizontal)
                .padding(.vertical, 10)
                
                // 2. Category Pills
                ScrollView(.horizontal, showsIndicators: false) {
                     HStack(spacing: 10) {
                         ForEach(ItemCategory.allCases) { category in
                             CategoryPill(category: category, isSelected: selectedCategory == category) {
                                 selectedCategory = category
                             }
                         }
                     }
                     .padding(.horizontal)
                     .padding(.bottom, 15)
                }
                
                // 3. Items Grid
                ScrollView {
                    LazyVGrid(columns: columns, spacing: 20) {
                        ForEach(filteredItems) { item in
                             NavigationLink(destination: MarketplaceDetailView(item: item)) {
                                ItemCardView(item: item)
                            }
                            .buttonStyle(PlainButtonStyle()) // Prevent blue tint on card
                        }
                    }
                    .padding()
                }
                .background(Color(.systemGray6)) // Grid background
            }
            .navigationTitle("二手市集")
            .navigationBarHidden(true) // Using custom top area
            .overlay(alignment: .bottomTrailing) { // Add Item Button
                Button {
                    showingAddItemSheet = true
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .resizable()
                        .frame(width: 50, height: 50)
                        .foregroundColor(.blue)
                        .background(.white)
                        .clipShape(Circle())
                        .shadow(radius: 5)
                        .padding()
                }
            }
            .sheet(isPresented: $showingAddItemSheet) {
                AddMarketplaceItemView(items: $items)
            }
        }
    }
}

// MARK: - Helper Views for List

// Category Pill Button
struct CategoryPill: View {
    let category: ItemCategory
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(category.rawValue)
                .font(.caption)
                .padding(.horizontal, 15)
                .padding(.vertical, 8)
                .background(isSelected ? Color.blue : Color(.systemGray4))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

// Item Card View
struct ItemCardView: View {
    let item: MarketplaceItem
    
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            // Image Placeholder
            ZStack {
                 RoundedRectangle(cornerRadius: 8)
                    .fill(Color(.systemGray5))
                    .aspectRatio(1.0, contentMode: .fit) // Square aspect ratio
                if let imageName = item.imageName {
                    Image(systemName: imageName) // Use system icons for mock
                        .resizable()
                        .scaledToFit()
                        .frame(width: 60, height: 60)
                        .foregroundColor(.gray)
                } else {
                    Image(systemName: "photo") // Default placeholder
                        .resizable()
                        .scaledToFit()
                        .frame(width: 60, height: 60)
                        .foregroundColor(.gray)
                }
            }
            
            Text(item.name)
                .font(.headline)
                .lineLimit(1)
            Text("NT$\\(item.price)")
                .font(.subheadline)
                .fontWeight(.bold)
                .foregroundColor(.orange)
            Text(item.condition)
                .font(.caption)
                .foregroundColor(.gray)
                .lineLimit(1)
        }
        .padding(10)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.05), radius: 4, y: 2)
    }
}

// MARK: - Detail View
struct MarketplaceDetailView: View {
    let item: MarketplaceItem
    @Environment(\.presentationMode) var presentationMode // For back button
    @State private var isFavorite: Bool = false // Mock favorite state

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) { // Use spacing 0 and manage padding manually
                
                // 1. Image Placeholder
                ZStack {
                    Rectangle()
                        .fill(Color(.systemGray5))
                        .frame(height: 250) // Height from prototype
                    if let imageName = item.imageName {
                        Image(systemName: imageName)
                            .resizable()
                            .scaledToFit()
                            .frame(height: 150) // Adjust size
                            .foregroundColor(.gray)
                    } else {
                        Image(systemName: "photo")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 150)
                            .foregroundColor(.gray)
                    }
                }
                .padding(.bottom, 20)
                
                // Content Padding
                VStack(alignment: .leading, spacing: 15) { // Add spacing here
                    // 2. Title and Price
                    Text(item.name)
                        .font(.system(size: 24, weight: .semibold))
                    
                    Text("NT$\\(item.price)")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.orange)
                        .padding(.bottom, 10) // Extra space below price

                    // 3. Seller Info
                    SectionHeader(title: "賣家資訊")
                    HStack(spacing: 15) {
                         Image(systemName: "person.crop.circle.fill") // Placeholder icon
                            .resizable()
                            .scaledToFit()
                            .frame(width: 50, height: 50)
                            .foregroundColor(.gray.opacity(0.6))
                        VStack(alignment: .leading) {
                            Text(item.sellerName).font(.headline)
                            Text(item.sellerDepartment).font(.subheadline).foregroundColor(.gray)
                        }
                        Spacer()
                    }
                    .padding(.bottom, 10)

                    // 4. Item Details
                    SectionHeader(title: "物品詳情")
                    VStack(alignment: .leading, spacing: 8) {
                        DetailRow(label: "商品狀態", value: item.condition)
                        DetailRow(label: "交易地點", value: item.tradeLocation)
                        DetailRow(label: "發布日期", value: item.postDate, dateStyle: .numeric) // Format date
                    }
                    .padding(.bottom, 10)
                    
                    // 5. Description
                    SectionHeader(title: "詳細描述")
                    Text(item.description)
                        .font(.body)
                        .lineSpacing(5)
                        .padding(.bottom, 20)
                        
                    // 6. Action Buttons
                    HStack(spacing: 15) {
                        Button {
                            isFavorite.toggle()
                        } label: {
                             Label(isFavorite ? "已收藏" : "收藏", systemImage: isFavorite ? "heart.fill" : "heart")
                                .font(.headline)
                                .foregroundColor(.blue)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(RoundedRectangle(cornerRadius: 12).stroke(Color.blue, lineWidth: 1))
                        }
                        
                        Button("聯絡賣家") {
                             // TODO: Implement chat functionality or contact method
                            print("聯絡賣家 clicked")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(12)
                    }
                }
                .padding(.horizontal) // Apply horizontal padding to content
            }
        }
        // Use inline navigation title and custom back button (optional)
        .navigationTitle("物品詳情")
        .navigationBarTitleDisplayMode(.inline)
        .navigationBarBackButtonHidden(true) // Hide default back button
        .toolbar { // Custom back button
             ToolbarItem(placement: .navigationBarLeading) {
                 Button { presentationMode.wrappedValue.dismiss() } label: {
                     Image(systemName: "arrow.left")
                 }
                 .tint(.primary) // Ensure button is visible
             }
        }
    }
}

// Helper View for Section Headers
struct SectionHeader: View {
    let title: String
    var body: some View {
        Text(title)
            .font(.title3)
            .fontWeight(.semibold)
            .padding(.bottom, 5)
    }
}

// Helper View for Detail Rows
struct DetailRow: View {
    let label: String
    let value: String
    
    init(label: String, value: String) {
        self.label = label
        self.value = value
    }
    
    // Overload for Date
    init(label: String, value: Date, dateStyle: Date.FormatStyle.DateStyle = .numeric) {
         self.label = label
         self.value = value.formatted(date: dateStyle, time: .omitted)
    }
    
    var body: some View {
        HStack(alignment: .top) {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.gray)
                .frame(width: 80, alignment: .leading) // Fixed width for label
            Text(value)
                .font(.subheadline)
            Spacer()
        }
    }
}

// MARK: - Add Item View
struct AddMarketplaceItemView: View {
    @Binding var items: [MarketplaceItem] // Receive binding to update list
    @Environment(\.presentationMode) var presentationMode

    // Form State
    @State private var itemName: String = ""
    @State private var selectedCategory: ItemCategory = .textbook
    @State private var price: String = "" // Use String for TextField
    @State private var condition: String = ""
    @State private var tradeLocation: String = ""
    @State private var description: String = ""
    // TODO: Add state for image picking
    // @State private var selectedImage: UIImage?

    var body: some View {
        NavigationView {
            Form {
                // Section 1: Image Upload (Placeholder)
                Section {
                    VStack(spacing: 10) {
                        Image(systemName: "camera.fill") // Placeholder icon
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        Text("點擊上傳商品照片")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 150)
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                    .overlay( // Dashed border overlay
                        RoundedRectangle(cornerRadius: 12)
                            .strokeBorder(style: StrokeStyle(lineWidth: 1, dash: [5]))
                            .foregroundColor(.gray)
                    )
                    // TODO: Add tap gesture for image picker
                    .onTapGesture {
                        print("Upload photo tapped")
                        // Show image picker
                    }
                }
                .listRowInsets(EdgeInsets()) // Remove Form's default padding
                .listRowBackground(Color.clear) // Make background transparent

                // Section 2: Item Info
                Section("商品資訊") {
                    TextField("商品名稱", text: $itemName)
                    Picker("類別", selection: $selectedCategory) {
                         // Exclude .all case for selection
                        ForEach(ItemCategory.allCases.filter { $0 != .all }) { category in
                            Text(category.rawValue).tag(category)
                        }
                    }
                    HStack { // Price with NT$
                         Text("NT$")
                        TextField("價格", text: $price)
                            .keyboardType(.numberPad)
                    }
                    TextField("商品狀態 (例如：9成新，無筆記)", text: $condition)
                }
                
                // Section 3: Transaction Details
                Section("交易資訊") {
                    TextField("交易地點 (例如：學校圖書館一樓)", text: $tradeLocation)
                }
                
                // Section 4: Description
                Section("詳細描述") {
                     TextField("請詳細描述您的商品", text: $description, axis: .vertical)
                        .lineLimit(5...)
                        .frame(minHeight: 100, alignment: .topLeading)
                }
            }
            .navigationTitle("發布二手物品")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("取消") { presentationMode.wrappedValue.dismiss() },
                trailing: Button("發布") { addItem() }.disabled(isFormInvalid) // Disable if form invalid
            )
        }
    }

    // Computed property to check if the form is valid for submission
    private var isFormInvalid: Bool {
        itemName.isEmpty || price.isEmpty || Int(price) == nil || condition.isEmpty || tradeLocation.isEmpty || description.isEmpty
    }

    // Function to add the item
    private func addItem() {
        guard let itemPrice = Int(price) else { return } // Ensure price is valid int
        
        let newItem = MarketplaceItem(
            name: itemName,
            price: itemPrice,
            description: description,
            condition: condition,
            category: selectedCategory,
            imageName: "photo", // Placeholder image
            sellerName: "目前使用者", // TODO: Get actual user name
            sellerDepartment: "測試系", // TODO: Get actual user dept
            postDate: Date(),
            tradeLocation: tradeLocation
        )
        items.append(newItem)
        presentationMode.wrappedValue.dismiss()
    }
}

// MARK: - Preview
#Preview {
    // Preview AddMarketplaceItemView with a State binding
    // Provide the initial 'value' and use the binding in the closure
    StatefulPreviewWrapper(value: []) { binding in
        AddMarketplaceItemView(items: binding)
    }
}

// Helper for Stateful Preview
struct StatefulPreviewWrapper<Value, Content: View>: View {
    @State var value: Value
    var content: (Binding<Value>) -> Content

    init(value: Value, content: @escaping (Binding<Value>) -> Content) {
        self._value = State(wrappedValue: value)
        self.content = content
    }

    var body: some View {
        content($value)
    }
} 