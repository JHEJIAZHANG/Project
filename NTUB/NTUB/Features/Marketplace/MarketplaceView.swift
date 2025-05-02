import SwiftUI

// MARK: - Marketplace Data Model
// Removed MarketplaceItem definition from here

// MARK: - Main Marketplace View (Container)
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
    
    // --- Mock Data (Updated to match MarketplaceItem model) ---
    @State private var items: [MarketplaceItem] = [
        MarketplaceItem(title: "資料庫系統概論 第五版", description: "課程用過一學期，保存良好，無筆記和劃線。", price: 350.0, sellerName: "林同學", sellerContact: nil, category: .textbook, condition: "9成新，無筆記", imageName: "book.closed.fill", postDate: Date().addingTimeInterval(-86400*2), isSold: false),
        MarketplaceItem(title: "MacBook Air 保護套", description: "多買的，全新未拆封。", price: 200.0, sellerName: "陳同學", sellerContact: "站內信", category: .electronics, condition: "全新未拆封", imageName: "laptopcomputer.and.arrow.down", postDate: Date().addingTimeInterval(-86400*1), isSold: false),
        MarketplaceItem(title: "計算機概論 2023版", description: "有做一些重點筆記，不介意者再來。", price: 400.0, sellerName: "王同學", sellerContact: nil, category: .textbook, condition: "8成新，有重點筆記", imageName: "book.closed.fill", postDate: Date().addingTimeInterval(-86400*3), isSold: false),
        MarketplaceItem(title: "Apple Pencil 第一代", description: "很少用，附贈一個筆套。", price: 2500.0, sellerName: "李同學", sellerContact: "校內面交", category: .electronics, condition: "9成新，附贈筆套", imageName: "applepencil", postDate: Date().addingTimeInterval(-86400*5), isSold: false)
    ]
    
    // Filtered items based on search and category
    var filteredItems: [MarketplaceItem] {
        items.filter { item in
            let categoryMatch = (selectedCategory == .all || item.category == selectedCategory)
            let searchMatch = searchText.isEmpty || item.title.localizedCaseInsensitiveContains(searchText) // Use title for search
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
                         ForEach(ItemCategory.allCases) { category in // Use ItemCategory
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
    let category: ItemCategory // Use ItemCategory
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
            
            Text(item.title) // Use title
                .font(.headline)
                .lineLimit(1)
            Text("NT$\(String(format: "%.0f", item.price))") // Format price from Double
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
                    Text(item.title) // Use title
                        .font(.system(size: 24, weight: .semibold))
                    
                    Text("NT$\(String(format: "%.0f", item.price))") // Format price from Double
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
                            // Text(item.sellerDepartment).font(.subheadline).foregroundColor(.gray) // Removed sellerDepartment
                            if let contact = item.sellerContact {
                                Text("聯絡方式: \(contact)").font(.subheadline).foregroundColor(.gray)
                            }
                        }
                        Spacer()
                    }
                    .padding(.bottom, 10)

                    // 4. Item Details
                    SectionHeader(title: "物品詳情")
                    VStack(alignment: .leading, spacing: 8) {
                        DetailRow(label: "商品狀態", value: item.condition)
                        // DetailRow(label: "交易地點", value: item.tradeLocation) // Removed tradeLocation
                         DetailRow(label: "物品分類", value: item.category.rawValue)
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
    @Binding var items: [MarketplaceItem]
    @Environment(\.presentationMode) var presentationMode

    // Form state
    @State private var itemTitle: String = ""
    @State private var itemDescription: String = ""
    @State private var itemPrice: String = ""
    @State private var itemCondition: String = ""
    @State private var selectedCategory: ItemCategory = .textbook // Use ItemCategory
    @State private var sellerContact: String = "" // Optional
    // TODO: Add State for image picking

    var body: some View {
        NavigationView {
            Form {
                Section("物品資訊") {
                    TextField("物品標題", text: $itemTitle)
                    TextField("詳細描述", text: $itemDescription, axis: .vertical).lineLimit(3...)
                    TextField("價格 (NT$)", text: $itemPrice)
                        .keyboardType(.decimalPad)
                    TextField("物品狀況 (例如：全新、九成新、有筆記)", text: $itemCondition)
                    Picker("物品分類", selection: $selectedCategory) { // Use ItemCategory
                         ForEach(ItemCategory.allCases.filter { $0 != .all }) { category in
                             Text(category.rawValue).tag(category)
                         }
                     }
                    TextField("聯絡方式 (選填，例如：手機、站內信)", text: $sellerContact)
                }
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
            }
            .navigationTitle("上架二手物品")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { presentationMode.wrappedValue.dismiss() }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("上架") {
                        addItem()
                    }
                    .disabled(itemTitle.isEmpty || itemPrice.isEmpty || Double(itemPrice) == nil) // Basic validation
                }
            }
        }
    }

    private func addItem() {
        guard let price = Double(itemPrice) else { return } // Validate price
        
        let newItem = MarketplaceItem(
            title: itemTitle,
            description: itemDescription,
            price: price,
            sellerName: "目前使用者", // TODO: Get actual user name
            sellerContact: sellerContact.isEmpty ? nil : sellerContact,
            category: selectedCategory,
            condition: itemCondition,
            imageName: nil, // TODO: Use picked image
            postDate: Date(),
            isSold: false
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