// EasyCart E-Commerce Core Application Logic
document.addEventListener('DOMContentLoaded', () => {
    // State Store
    const state = {
        products: [],
        categories: [],
        currentCategory: 'All',
        searchQuery: '',
        sortBy: 'default',
        inStockOnly: false,
        priceFilter: 'all',
        cart: JSON.parse(localStorage.getItem('easycart_cart') || '[]'),
        couponCode: localStorage.getItem('easycart_coupon') || null,
        cartCalculation: null,
        currentUser: null,
        theme: localStorage.getItem('easycart_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    };

    // DOM Elements Cache
    const el = {
        html: document.documentElement,
        themeToggle: document.getElementById('theme-toggle'),
        themeIcon: document.getElementById('theme-icon'),
        themeText: document.getElementById('theme-text'),
        homeLogoBtn: document.getElementById('home-logo-btn'),
        globalSearch: document.getElementById('global-search'),
        searchBtn: document.getElementById('search-btn'),
        headerCartBtn: document.getElementById('header-cart-btn'),
        cartBadge: document.getElementById('cart-badge'),
        cartTotalHeader: document.getElementById('cart-total-header'),
        categoryPills: document.querySelectorAll('.cat-pill'),
        catalogueTitle: document.getElementById('current-catalogue-title'),
        productCountDisplay: document.getElementById('product-count-display'),
        instockFilter: document.getElementById('instock-filter'),
        priceFilter: document.getElementById('price-filter'),
        sortSelect: document.getElementById('sort-select'),
        productGrid: document.getElementById('product-grid'),
        emptyProductsState: document.getElementById('empty-products-state'),
        resetFiltersBtn: document.getElementById('reset-filters-btn'),
        categoryBannersSection: document.getElementById('category-banners-section'),
        storefrontProductsView: document.getElementById('storefront-products-view'),
        backToBannersBtn: document.getElementById('back-to-banners-btn'),

        // Product Modal
        productModal: document.getElementById('product-modal'),
        closeProductModal: document.getElementById('close-product-modal'),
        productDetailContent: document.getElementById('product-detail-content'),

        // Cart Drawer
        cartDrawer: document.getElementById('cart-drawer'),
        closeCartBtn: document.getElementById('close-cart-btn'),
        cartDrawerCount: document.getElementById('cart-drawer-count'),
        drawerCartEmpty: document.getElementById('drawer-cart-empty'),
        drawerCartContent: document.getElementById('drawer-cart-content'),
        cartItemsContainer: document.getElementById('cart-items-container'),
        couponInput: document.getElementById('coupon-input'),
        applyCouponBtn: document.getElementById('apply-coupon-btn'),
        appliedCouponPill: document.getElementById('applied-coupon-pill'),
        appliedCouponText: document.getElementById('applied-coupon-text'),
        removeCouponBtn: document.getElementById('remove-coupon-btn'),
        summarySubtotal: document.getElementById('summary-subtotal'),
        summaryDiscountRow: document.getElementById('summary-discount-row'),
        summaryDiscount: document.getElementById('summary-discount'),
        summaryDelivery: document.getElementById('summary-delivery'),
        summaryTotal: document.getElementById('summary-total'),
        proceedCheckoutBtn: document.getElementById('proceed-checkout-btn'),
        clearCartBtn: document.getElementById('clear-cart-btn'),
        startShoppingBtn: document.getElementById('start-shopping-btn'),

        // Checkout Modal
        checkoutModal: document.getElementById('checkout-modal'),
        closeCheckoutModal: document.getElementById('close-checkout-modal'),
        checkoutForm: document.getElementById('checkout-form'),
        shipName: document.getElementById('ship-name'),
        shipPhone: document.getElementById('ship-phone'),
        shipEmail: document.getElementById('ship-email'),
        shipAddress: document.getElementById('ship-address'),
        shipCity: document.getElementById('ship-city'),
        shipState: document.getElementById('ship-state'),
        shipPin: document.getElementById('ship-pin'),
        checkoutReviewItems: document.getElementById('checkout-review-items'),
        checkoutSubtotal: document.getElementById('checkout-subtotal'),
        checkoutDiscountRow: document.getElementById('checkout-discount-row'),
        checkoutDiscount: document.getElementById('checkout-discount'),
        checkoutDelivery: document.getElementById('checkout-delivery'),
        checkoutGrandTotal: document.getElementById('checkout-grand-total'),
        checkoutBtnAmount: document.getElementById('checkout-btn-amount'),

        // Invoice Modal
        invoiceModal: document.getElementById('invoice-modal'),
        invoiceContinueBtn: document.getElementById('invoice-continue-btn'),
        invOrderId: document.getElementById('inv-order-id'),
        invOrderDate: document.getElementById('inv-order-date'),
        invCustName: document.getElementById('inv-cust-name'),
        invCustAddress: document.getElementById('inv-cust-address'),
        invCustCity: document.getElementById('inv-cust-city'),
        invCustPhone: document.getElementById('inv-cust-phone'),
        invCustEmail: document.getElementById('inv-cust-email'),
        invPaymentMethod: document.getElementById('inv-payment-method'),
        invItemsBody: document.getElementById('inv-items-body'),
        invSubtotal: document.getElementById('inv-subtotal'),
        invDiscountRow: document.getElementById('inv-discount-row'),
        invDiscount: document.getElementById('inv-discount'),
        invDelivery: document.getElementById('inv-delivery'),
        invGrandTotal: document.getElementById('inv-grand-total'),

        // Toast
        toast: document.getElementById('toast-notification'),
        toastMessage: document.getElementById('toast-message'),

        // Auth & Account Modal
        authModal: document.getElementById('auth-modal'),
        closeAuthModal: document.getElementById('close-auth-modal'),
        tabLoginBtn: document.getElementById('tab-login-btn'),
        tabRegisterBtn: document.getElementById('tab-register-btn'),
        loginPane: document.getElementById('login-pane'),
        registerPane: document.getElementById('register-pane'),
        loginForm: document.getElementById('login-form'),
        registerForm: document.getElementById('register-form'),
        loginEmail: document.getElementById('login-email'),
        loginPassword: document.getElementById('login-password'),
        regName: document.getElementById('reg-name'),
        regEmail: document.getElementById('reg-email'),
        regPassword: document.getElementById('reg-password'),

        headerAccountBtn: document.getElementById('header-account-btn'),
        accountGreeting: document.getElementById('account-greeting'),
        accountStatusLabel: document.getElementById('account-status-label'),
        accountModal: document.getElementById('account-modal'),
        closeAccountModal: document.getElementById('close-account-modal'),
        accountAvatarInitials: document.getElementById('account-avatar-initials'),
        accountProfileName: document.getElementById('account-profile-name'),
        accountProfileEmail: document.getElementById('account-profile-email'),
        accountLogoutBtn: document.getElementById('account-logout-btn')
    };

    // ----------------- Theme Switcher -----------------
    const applyTheme = (theme) => {
        state.theme = theme;
        el.html.setAttribute('data-theme', theme);
        localStorage.setItem('easycart_theme', theme);
        if (theme === 'dark') {
            el.themeIcon.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
            el.themeText.textContent = 'Light Mode';
        } else {
            el.themeIcon.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
            el.themeText.textContent = 'Dark Mode';
        }
    };

    el.themeToggle.addEventListener('click', () => {
        applyTheme(state.theme === 'dark' ? 'light' : 'dark');
    });
    applyTheme(state.theme);

    // ----------------- Toast Notifications -----------------
    let toastTimeout = null;
    window.showToast = (msg) => {
        if (toastTimeout) clearTimeout(toastTimeout);
        el.toastMessage.textContent = msg;
        el.toast.classList.remove('hidden');
        toastTimeout = setTimeout(() => {
            el.toast.classList.add('hidden');
        }, 3500);
    };

    window.closeToast = () => {
        el.toast.classList.add('hidden');
    };

    // ----------------- Product Fetching & Filtering -----------------
    const fetchProducts = async () => {
        const params = new URLSearchParams();
        if (state.currentCategory && state.currentCategory !== 'All') {
            params.append('category', state.currentCategory);
        }
        if (state.searchQuery) {
            params.append('search', state.searchQuery);
        }
        if (state.sortBy && state.sortBy !== 'default') {
            params.append('sort', state.sortBy);
        }
        if (state.inStockOnly) {
            params.append('in_stock', 'true');
        }
        if (state.priceFilter === '0-500') {
            params.append('min_price', '0');
            params.append('max_price', '500');
        } else if (state.priceFilter === '500-1500') {
            params.append('min_price', '500');
            params.append('max_price', '1500');
        } else if (state.priceFilter === '1500-5000') {
            params.append('min_price', '1500');
            params.append('max_price', '5000');
        } else if (state.priceFilter === '5000+') {
            params.append('min_price', '5000');
        }

        try {
            const res = await fetch(`/api/products?${params.toString()}`);
            state.products = await res.json();
            renderCatalog();
        } catch (err) {
            showToast('Unable to connect to EasyCart server.');
        }
    };

    // Helper: Resolve Image URL with guaranteed offline fallback
    const getProductImage = (product) => {
        if (product.image_url) {
            return product.image_url;
        }
        if (product.image) {
            return product.image;
        }
        const svgId = (product.id >= 1 && product.id <= 25) ? product.id : 1;
        return `/static/images/p${svgId}.svg`;
    };

    // Helper: Local SVG Fallback for onerror
    const getFallbackImage = (product) => {
        const svgId = (product && product.id >= 1 && product.id <= 25) ? product.id : 1;
        return `/static/images/p${svgId}.svg`;
    };

    // Render Product Catalog
    const renderCatalog = () => {
        el.catalogueTitle.textContent = state.searchQuery 
            ? `Search: "${state.searchQuery}"` 
            : (state.currentCategory === 'All' ? 'All Products' : state.currentCategory);
        
        el.productCountDisplay.textContent = `Showing ${state.products.length} product${state.products.length === 1 ? '' : 's'}`;
        
        // Visibility Rules:
        // When state.currentCategory === 'All' AND there is NO search query:
        // Show ONLY the stacked banners. Keep the products view hidden.
        // When a specific category is selected or a search is active:
        // Hide the banners. Show the products view.
        const isBrowsingProducts = (state.currentCategory !== 'All') || (state.searchQuery.length > 0);

        if (el.categoryBannersSection) {
            if (isBrowsingProducts) {
                el.categoryBannersSection.classList.add('hidden');
            } else {
                el.categoryBannersSection.classList.remove('hidden');
            }
        }

        if (el.storefrontProductsView) {
            if (isBrowsingProducts) {
                el.storefrontProductsView.classList.remove('hidden');
            } else {
                el.storefrontProductsView.classList.add('hidden');
                // Clean up grid when in home/banners mode
                el.productGrid.innerHTML = '';
                return;
            }
        }

        // Determine if empty because of category with no products (no filters applied)
        const isFiltered = state.searchQuery || state.inStockOnly || state.priceFilter !== 'all';
        const isCategoryEmpty = state.currentCategory !== 'All' && !isFiltered;
        
        const emptyCategory = document.getElementById('empty-category-state');
        const emptyProducts = document.getElementById('empty-products-state');

        if (state.products.length === 0) {
            el.productGrid.innerHTML = '';
            if (emptyCategory) emptyCategory.classList.add('hidden');
            if (emptyProducts) emptyProducts.classList.add('hidden');
            if (isCategoryEmpty && emptyCategory) {
                emptyCategory.classList.remove('hidden');
            } else if (emptyProducts) {
                emptyProducts.classList.remove('hidden');
            }
            return;
        }

        // Hide empty states when we have products
        if (emptyCategory) emptyCategory.classList.add('hidden');
        if (emptyProducts) emptyProducts.classList.add('hidden');

        el.productGrid.innerHTML = state.products.map(product => {
            const discountPct = product.original_price && product.original_price > product.price
                ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
                : 0;

            const inCartItem = state.cart.find(i => i.id === product.id);
            const inCartQty = inCartItem ? inCartItem.quantity : 0;
            const remaining = product.quantity - inCartQty;
            const isSoldOut = remaining <= 0;
            const imgSrc = getProductImage(product);
            const fallbackSrc = getFallbackImage(product);

            let stockBadge = '<span class="stock-status-pill stock-in">In Stock</span>';
            if (product.quantity <= 0) {
                stockBadge = '<span class="stock-status-pill stock-out">Out of Stock</span>';
            } else if (product.quantity <= 3) {
                stockBadge = `<span class="stock-status-pill stock-low">Only ${product.quantity} left</span>`;
            }

            return `
                <article class="product-card" data-id="${product.id}">
                    <div class="card-image-wrapper" onclick="window.openProductDetail(${product.id})">
                        <img src="${imgSrc}" alt="${escapeHtml(product.name)}" loading="lazy" onerror="this.onerror=null;this.src='${fallbackSrc}';">
                        ${discountPct > 0 ? `<span class="discount-badge-tag">${discountPct}% OFF</span>` : ''}
                    </div>
                    <div class="card-details">
                        <span class="card-category">${escapeHtml(product.category)}</span>
                        <h3 class="card-title" onclick="window.openProductDetail(${product.id})">${escapeHtml(product.name)}</h3>
                        
                        <div class="card-rating-row">
                            <span class="rating-pill">★ ${product.rating.toFixed(1)}</span>
                            <span class="rating-count-text">(${product.rating_count})</span>
                        </div>

                        <div class="card-pricing">
                            <span class="selling-price">₹${product.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                            ${product.original_price ? `<span class="original-price">₹${product.original_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>` : ''}
                        </div>

                        ${stockBadge}

                        <div class="card-actions">
                            <button type="button" class="btn btn-primary btn-cart-action" onclick="window.addToCart(${product.id})" ${isSoldOut ? 'disabled' : ''}>
                                ${isSoldOut ? 'Sold Out' : '+ Add to Cart'}
                            </button>
                            <button type="button" class="btn btn-secondary btn-sm" onclick="window.openProductDetail(${product.id})">
                                Details
                            </button>
                        </div>
                    </div>
                </article>
            `;
        }).join('');
    };

    // Category Selector
    window.selectCategory = (cat) => {
        state.currentCategory = cat;
        state.searchQuery = '';
        el.globalSearch.value = '';
        el.categoryPills.forEach(pill => {
            pill.classList.toggle('active', pill.getAttribute('data-category') === cat);
        });

        // Banner and Product Grid Visibility Control
        if (cat === 'All') {
            if (el.categoryBannersSection) el.categoryBannersSection.classList.remove('hidden');
            if (el.storefrontProductsView) el.storefrontProductsView.classList.add('hidden');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            if (el.categoryBannersSection) el.categoryBannersSection.classList.add('hidden');
            if (el.storefrontProductsView) el.storefrontProductsView.classList.remove('hidden');
            fetchProducts();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    // Alias for requirement compatibility
    window.filterByCategory = window.selectCategory;

    el.categoryPills.forEach(pill => {
        pill.addEventListener('click', () => {
            selectCategory(pill.getAttribute('data-category'));
        });
    });

    // Search Handlers
    const executeSearch = () => {
        state.searchQuery = el.globalSearch.value.trim();
        fetchProducts();
    };

    el.searchBtn.addEventListener('click', executeSearch);
    el.globalSearch.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') executeSearch();
    });

    el.homeLogoBtn.addEventListener('click', (e) => {
        e.preventDefault();
        selectCategory('All');
    });

    // Sort & Filters
    el.sortSelect.addEventListener('change', () => {
        state.sortBy = el.sortSelect.value;
        fetchProducts();
    });

    el.instockFilter.addEventListener('change', () => {
        state.inStockOnly = el.instockFilter.checked;
        fetchProducts();
    });

    el.priceFilter.addEventListener('change', () => {
        state.priceFilter = el.priceFilter.value;
        fetchProducts();
    });

    el.resetFiltersBtn.addEventListener('click', () => {
        state.searchQuery = '';
        state.currentCategory = 'All';
        state.sortBy = 'default';
        state.inStockOnly = false;
        state.priceFilter = 'all';

        el.globalSearch.value = '';
        el.sortSelect.value = 'default';
        el.instockFilter.checked = false;
        el.priceFilter.value = 'all';
        el.categoryPills.forEach(p => p.classList.toggle('active', p.getAttribute('data-category') === 'All'));

        fetchProducts();
    });

    // "View All Products" button in category empty state
    const viewAllBtn = document.getElementById('view-all-btn');
    if (viewAllBtn) {
        viewAllBtn.addEventListener('click', () => {
            selectCategory('All');
        });
    }

    // "Back to Banners" button in toolbar
    if (el.backToBannersBtn) {
        el.backToBannersBtn.addEventListener('click', () => {
            selectCategory('All');
        });
    }

    // ----------------- Product Detail Modal -----------------
    window.openProductDetail = async (productId) => {
        try {
            const res = await fetch(`/api/products/${productId}`);
            if (!res.ok) throw new Error('Product not found');
            const data = await res.json();
            const product = data.product;
            const related = data.related || [];

            const discountPct = product.original_price && product.original_price > product.price
                ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
                : 0;

            const inCartItem = state.cart.find(i => i.id === product.id);
            const inCartQty = inCartItem ? inCartItem.quantity : 0;
            const remaining = product.quantity - inCartQty;
            const isSoldOut = remaining <= 0;

            const imgSrc = getProductImage(product);
            const fallbackSrc = getFallbackImage(product);

            el.productDetailContent.innerHTML = `
                <div class="modal-img-col">
                    <img src="${imgSrc}" alt="${escapeHtml(product.name)}" onerror="this.onerror=null;this.src='${fallbackSrc}';">
                    ${discountPct > 0 ? `<span class="discount-badge-tag">${discountPct}% OFF</span>` : ''}
                </div>
                <div class="modal-info-col">
                    <span class="detail-category">${escapeHtml(product.category)}</span>
                    <h2 class="detail-title">${escapeHtml(product.name)}</h2>

                    <div class="card-rating-row">
                        <span class="rating-pill">★ ${product.rating.toFixed(1)}</span>
                        <span class="rating-count-text">${product.rating_count} verified ratings</span>
                    </div>

                    <div class="detail-pricing">
                        <span class="detail-selling-price">₹${product.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                        ${product.original_price ? `<span class="detail-original-price">₹${product.original_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>` : ''}
                        ${discountPct > 0 ? `<span class="detail-discount-tag">Save ${discountPct}%</span>` : ''}
                    </div>

                    <p class="detail-description">${escapeHtml(product.description)}</p>

                    <div class="detail-stock-box">
                        ${product.quantity > 0 
                            ? `<span class="stock-in">✓ In Stock (${product.quantity} available units)</span>` 
                            : `<span class="stock-out">✕ Currently Out of Stock</span>`}
                    </div>

                    <div class="detail-actions-row">
                        <div class="quantity-stepper">
                            <button type="button" class="stepper-btn" onclick="stepDetailQty(-1)">-</button>
                            <span class="stepper-val" id="detail-qty-val">1</span>
                            <button type="button" class="stepper-btn" onclick="stepDetailQty(1)">+</button>
                        </div>
                        <button type="button" class="btn btn-primary btn-lg flex-1" onclick="addDetailToCart(${product.id})" ${isSoldOut ? 'disabled' : ''}>
                            ${isSoldOut ? 'Sold Out' : '+ Add to Cart'}
                        </button>
                    </div>
                </div>

                ${related.length > 0 ? `
                    <div class="related-section">
                        <h4 class="related-title">Related in ${escapeHtml(product.category)}</h4>
                        <div class="related-grid">
                            ${related.map(r => `
                                <div class="related-card" onclick="openProductDetail(${r.id})">
                                    <img src="${getProductImage(r)}" alt="${escapeHtml(r.name)}" onerror="this.onerror=null;this.src='${getFallbackImage(r)}';">
                                    <div class="related-card-name">${escapeHtml(r.name)}</div>
                                    <div class="related-card-price">₹${r.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            `;

            el.productModal.classList.remove('hidden');
        } catch (err) {
            showToast('Failed to load product details.');
        }
    };

    let detailSelectedQty = 1;
    window.stepDetailQty = (delta) => {
        detailSelectedQty = Math.max(1, detailSelectedQty + delta);
        const display = document.getElementById('detail-qty-val');
        if (display) display.textContent = detailSelectedQty;
    };

    window.addDetailToCart = (productId) => {
        addToCart(productId, detailSelectedQty);
        el.productModal.classList.add('hidden');
        detailSelectedQty = 1;
    };

    el.closeProductModal.addEventListener('click', () => {
        el.productModal.classList.add('hidden');
    });

    // ----------------- Shopping Cart Controller -----------------
    window.addToCart = (productId, qty = 1) => {
        const product = state.products.find(p => p.id === productId);
        const existing = state.cart.find(i => i.id === productId);

        const currentQtyInCart = existing ? existing.quantity : 0;
        const availableStock = product ? product.quantity : 99;

        if (currentQtyInCart + qty > availableStock) {
            showToast(`Cannot add more. Only ${availableStock} unit(s) available in stock.`);
            return;
        }

        if (existing) {
            existing.quantity += qty;
        } else {
            state.cart.push({
                id: productId,
                quantity: qty
            });
        }

        saveCart();
        syncCartWithServer();
        showToast(`Added to cart!`);
    };

    window.updateCartItemQty = (productId, delta) => {
        const item = state.cart.find(i => i.id === productId);
        if (!item) return;

        const newQty = item.quantity + delta;
        if (newQty <= 0) {
            state.cart = state.cart.filter(i => i.id !== productId);
        } else {
            item.quantity = newQty;
        }

        saveCart();
        syncCartWithServer();
    };

    window.removeCartItem = (productId) => {
        state.cart = state.cart.filter(i => i.id !== productId);
        saveCart();
        syncCartWithServer();
    };

    const clearCart = () => {
        if (state.cart.length === 0) return;
        if (confirm('Are you sure you want to empty your shopping cart?')) {
            state.cart = [];
            state.couponCode = null;
            localStorage.removeItem('easycart_coupon');
            saveCart();
            syncCartWithServer();
            showToast('Shopping cart cleared.');
        }
    };

    el.clearCartBtn.addEventListener('click', clearCart);

    const saveCart = () => {
        localStorage.setItem('easycart_cart', JSON.stringify(state.cart));
    };

    // Server-Side Cart Calculation Synchronization
    const syncCartWithServer = async () => {
        if (state.cart.length === 0) {
            state.cartCalculation = {
                items: [],
                subtotal: 0,
                discount: 0,
                delivery_fee: 0,
                total: 0,
                applied_coupon: null
            };
            renderCartUI();
            renderCatalog();
            return;
        }

        try {
            const res = await fetch('/api/cart/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    items: state.cart,
                    coupon_code: state.couponCode
                })
            });

            const data = await res.json();
            state.cartCalculation = data;

            // Handle stock error notifications if stock dropped
            if (data.stock_errors && data.stock_errors.length > 0) {
                showToast(data.stock_errors[0]);
            }

            renderCartUI();
            renderCatalog();
        } catch (err) {
            showToast('Unable to recalculate cart with server.');
        }
    };

    // Render Cart Drawer UI
    const renderCartUI = () => {
        const calc = state.cartCalculation || { items: [], subtotal: 0, discount: 0, delivery_fee: 0, total: 0 };
        const totalItemsCount = state.cart.reduce((sum, i) => sum + i.quantity, 0);

        // Header and Badge updates
        el.cartBadge.textContent = totalItemsCount;
        el.cartDrawerCount.textContent = totalItemsCount;
        el.cartTotalHeader.textContent = `₹${calc.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

        if (state.cart.length === 0) {
            el.drawerCartEmpty.classList.remove('hidden');
            el.drawerCartContent.classList.add('hidden');
            return;
        }

        el.drawerCartEmpty.classList.add('hidden');
        el.drawerCartContent.classList.remove('hidden');

        // Render Cart Items
        el.cartItemsContainer.innerHTML = calc.items.map(item => `
            <div class="cart-item-card">
                <img src="${getProductImage(item)}" alt="${escapeHtml(item.name)}" class="cart-item-img" onerror="this.onerror=null;this.src='${getFallbackImage(item)}';">
                <div class="cart-item-info">
                    <h4 class="cart-item-name">${escapeHtml(item.name)}</h4>
                    <div class="cart-item-price-row">
                        <span class="cart-item-price">₹${item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                        ${item.original_price ? `<span class="original-price">₹${item.original_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>` : ''}
                    </div>
                    <div class="cart-item-controls">
                        <div class="quantity-stepper">
                            <button type="button" class="stepper-btn" onclick="updateCartItemQty(${item.id}, -1)">-</button>
                            <span class="stepper-val">${item.quantity}</span>
                            <button type="button" class="stepper-btn" onclick="updateCartItemQty(${item.id}, 1)" ${item.quantity >= item.max_stock ? 'disabled' : ''}>+</button>
                        </div>
                        <button type="button" class="cart-remove-link" onclick="removeCartItem(${item.id})">Remove</button>
                    </div>
                </div>
            </div>
        `).join('');

        // Render Price Breakdown
        el.summarySubtotal.textContent = `₹${calc.subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        
        if (calc.discount > 0) {
            el.summaryDiscountRow.classList.remove('hidden');
            el.summaryDiscount.textContent = `-₹${calc.discount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        } else {
            el.summaryDiscountRow.classList.add('hidden');
        }

        if (calc.delivery_fee === 0) {
            el.summaryDelivery.innerHTML = '<span class="text-success" style="color:var(--accent-success);font-weight:700;">FREE</span>';
        } else {
            el.summaryDelivery.textContent = `₹${calc.delivery_fee.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        }

        el.summaryTotal.textContent = `₹${calc.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

        // Render Applied Coupon Pill
        if (calc.applied_coupon) {
            el.appliedCouponPill.classList.remove('hidden');
            el.appliedCouponText.textContent = `✓ ${calc.applied_coupon.code}: ${calc.applied_coupon.description}`;
            el.couponInput.value = calc.applied_coupon.code;
        } else {
            el.appliedCouponPill.classList.add('hidden');
            if (!state.couponCode) el.couponInput.value = '';
        }
    };

    // Coupon Actions
    window.applyCouponCode = (code) => {
        state.couponCode = code.trim().toUpperCase();
        localStorage.setItem('easycart_coupon', state.couponCode);
        syncCartWithServer();
    };

    window.copyCouponCode = (code) => {
        applyCouponCode(code);
        openCartDrawer();
        showToast(`Coupon "${code}" applied to cart!`);
    };

    el.applyCouponBtn.addEventListener('click', () => {
        const code = el.couponInput.value.trim();
        if (!code) {
            showToast('Please enter a coupon code.');
            return;
        }
        applyCouponCode(code);
    });

    el.removeCouponBtn.addEventListener('click', () => {
        state.couponCode = null;
        localStorage.removeItem('easycart_coupon');
        el.couponInput.value = '';
        syncCartWithServer();
        showToast('Coupon removed.');
    });

    // Drawer Visibility
    const openCartDrawer = () => {
        syncCartWithServer();
        el.cartDrawer.classList.remove('hidden');
    };

    const closeCartDrawer = () => {
        el.cartDrawer.classList.add('hidden');
    };

    el.headerCartBtn.addEventListener('click', openCartDrawer);
    el.closeCartBtn.addEventListener('click', closeCartDrawer);
    el.startShoppingBtn.addEventListener('click', () => {
        closeCartDrawer();
        window.scrollTo({ top: 200, behavior: 'smooth' });
    });

    // ----------------- Authentication & Account Management -----------------
    const updateAuthUI = (user) => {
        state.currentUser = user;
        if (user) {
            el.accountGreeting.textContent = `Hello, ${user.name.split(' ')[0]}`;
            el.accountStatusLabel.textContent = 'Account';
            el.accountProfileName.textContent = user.name;
            el.accountProfileEmail.textContent = user.email;
            
            const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'SS';
            el.accountAvatarInitials.textContent = initials;
            
            // Pre-fill checkout form with user details
            if (el.shipName && !el.shipName.value) el.shipName.value = user.name;
            if (el.shipEmail && !el.shipEmail.value) el.shipEmail.value = user.email;
        } else {
            el.accountGreeting.textContent = 'Hello, Sign In';
            el.accountStatusLabel.textContent = 'Account';
        }
    };

    const checkAuthStatus = async () => {
        try {
            const res = await fetch('/api/auth/me');
            const data = await res.json();
            if (data.authenticated && data.user) {
                updateAuthUI(data.user);
            } else {
                updateAuthUI(null);
            }
        } catch (err) {
            console.error('Failed to verify session:', err);
            updateAuthUI(null);
        }
    };

    const openAuthModal = (targetTab = 'login') => {
        if (targetTab === 'register') {
            el.tabRegisterBtn.classList.add('active');
            el.tabLoginBtn.classList.remove('active');
            el.registerPane.classList.remove('hidden');
            el.loginPane.classList.add('hidden');
        } else {
            el.tabLoginBtn.classList.add('active');
            el.tabRegisterBtn.classList.remove('active');
            el.loginPane.classList.remove('hidden');
            el.registerPane.classList.add('hidden');
        }
        el.authModal.classList.remove('hidden');
    };

    const closeAuthModal = () => {
        el.authModal.classList.add('hidden');
    };

    el.headerAccountBtn.addEventListener('click', () => {
        if (state.currentUser) {
            el.accountModal.classList.remove('hidden');
        } else {
            openAuthModal('login');
        }
    });

    if (el.closeAuthModal) el.closeAuthModal.addEventListener('click', closeAuthModal);
    if (el.closeAccountModal) el.closeAccountModal.addEventListener('click', () => el.accountModal.classList.add('hidden'));

    if (el.tabLoginBtn) {
        el.tabLoginBtn.addEventListener('click', () => {
            el.tabLoginBtn.classList.add('active');
            el.tabRegisterBtn.classList.remove('active');
            el.loginPane.classList.remove('hidden');
            el.registerPane.classList.add('hidden');
        });
    }

    if (el.tabRegisterBtn) {
        el.tabRegisterBtn.addEventListener('click', () => {
            el.tabRegisterBtn.classList.add('active');
            el.tabLoginBtn.classList.remove('active');
            el.registerPane.classList.remove('hidden');
            el.loginPane.classList.add('hidden');
        });
    }

    // Login Submission
    if (el.loginForm) {
        el.loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = el.loginEmail.value.trim();
            const password = el.loginPassword.value.trim();
            if (!email) {
                showToast('Please enter an email address.');
                return;
            }

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (res.ok && data.success) {
                    updateAuthUI(data.user);
                    closeAuthModal();
                    showToast(data.message || `Welcome, ${data.user.name}!`);
                    
                    // If user was prompted during checkout, proceed
                    if (pendingCheckoutResume) {
                        pendingCheckoutResume = false;
                        startCheckoutFlow();
                    }
                } else {
                    showToast(data.error || 'Login failed.');
                }
            } catch (err) {
                console.error('Login error:', err);
                showToast('Network error during login.');
            }
        });
    }

    // Registration Submission
    if (el.registerForm) {
        el.registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = el.regName.value.trim();
            const email = el.regEmail.value.trim();
            const password = el.regPassword.value.trim();
            if (!email) {
                showToast('Please enter an email address.');
                return;
            }

            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                const data = await res.json();
                if (res.ok && data.success) {
                    updateAuthUI(data.user);
                    closeAuthModal();
                    showToast(`Account created! Welcome, ${data.user.name}!`);
                    
                    if (pendingCheckoutResume) {
                        pendingCheckoutResume = false;
                        startCheckoutFlow();
                    }
                } else {
                    showToast(data.error || 'Registration failed.');
                }
            } catch (err) {
                console.error('Registration error:', err);
                showToast('Network error during registration.');
            }
        });
    }

    // Logout
    if (el.accountLogoutBtn) {
        el.accountLogoutBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                updateAuthUI(null);
                el.accountModal.classList.add('hidden');
                showToast('You have signed out of EasyCart.');
            } catch (err) {
                console.error('Logout error:', err);
            }
        });
    }

    // ----------------- Checkout Flow with Auth Guard -----------------
    let pendingCheckoutResume = false;

    const startCheckoutFlow = () => {
        closeCartDrawer();
        const calc = state.cartCalculation || { items: [], subtotal: 0, discount: 0, delivery_fee: 0, total: 0 };

        // Pre-fill user data
        if (state.currentUser) {
            el.shipName.value = state.currentUser.name || 'Shraddha Singh';
            el.shipEmail.value = state.currentUser.email || 'shraddha.singh@gmail.com';
        } else {
            el.shipName.value = 'Shraddha Singh';
            el.shipEmail.value = 'shraddha.singh@gmail.com';
        }

        // Populate Order Review
        el.checkoutReviewItems.innerHTML = calc.items.map(item => `
            <div class="review-item-row">
                <span>${escapeHtml(item.name)} &times; ${item.quantity}</span>
                <strong>₹${item.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
            </div>
        `).join('');

        el.checkoutSubtotal.textContent = `₹${calc.subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        if (calc.discount > 0) {
            el.checkoutDiscountRow.classList.remove('hidden');
            el.checkoutDiscount.textContent = `-₹${calc.discount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        } else {
            el.checkoutDiscountRow.classList.add('hidden');
        }

        el.checkoutDelivery.textContent = calc.delivery_fee === 0 ? 'FREE' : `₹${calc.delivery_fee.toFixed(2)}`;
        el.checkoutGrandTotal.textContent = `₹${calc.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        el.checkoutBtnAmount.textContent = `₹${calc.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

        el.checkoutModal.classList.remove('hidden');
    };

    el.proceedCheckoutBtn.addEventListener('click', () => {
        if (state.cart.length === 0) return;
        
        // Guard step: Check if user is logged in
        if (!state.currentUser) {
            pendingCheckoutResume = true;
            closeCartDrawer();
            openAuthModal('login');
            showToast('Please sign in with your email to proceed to checkout.');
            return;
        }

        startCheckoutFlow();
    });

    el.closeCheckoutModal.addEventListener('click', () => {
        el.checkoutModal.classList.add('hidden');
    });

    // Handle Checkout Submit
    el.checkoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const deliveryInfo = {
            name: el.shipName.value.trim(),
            phone: el.shipPhone.value.trim(),
            email: el.shipEmail.value.trim(),
            address: el.shipAddress.value.trim(),
            city: el.shipCity.value.trim(),
            state: el.shipState.value.trim(),
            postal_code: el.shipPin.value.trim()
        };

        const paymentMethodEl = document.querySelector('input[name="payment_method"]:checked');
        const paymentMethod = paymentMethodEl ? paymentMethodEl.value : 'Cash on Delivery (Demo)';

        const submitBtn = document.getElementById('place-order-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing Order...';

        try {
            const res = await fetch('/api/cart/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    items: state.cart,
                    coupon_code: state.couponCode,
                    delivery: deliveryInfo,
                    payment_method: paymentMethod
                })
            });

            const data = await res.json();
            if (res.ok && data.success) {
                // Clear Cart
                state.cart = [];
                state.couponCode = null;
                localStorage.removeItem('easycart_cart');
                localStorage.removeItem('easycart_coupon');

                // Render Printable Invoice Modal
                renderInvoice(data.order_details);

                el.checkoutModal.classList.add('hidden');
                el.invoiceModal.classList.remove('hidden');

                // Refresh product inventory from server
                fetchProducts();
                syncCartWithServer();
            } else {
                showToast(data.error || 'Failed to place order.');
            }
        } catch (err) {
            showToast('Network error during checkout.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `Confirm & Place Order (<span id="checkout-btn-amount">₹${state.cartCalculation ? state.cartCalculation.total.toFixed(2) : '0.00'}</span>)`;
        }
    });

    // Render Order Invoice
    const renderInvoice = (order) => {
        el.invOrderId.textContent = order.order_id;
        el.invOrderDate.textContent = new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });
        el.invCustName.textContent = order.customer.name;
        el.invCustAddress.textContent = order.customer.address;
        el.invCustCity.textContent = `${order.customer.city}, ${order.customer.state} - ${order.customer.postal_code}`;
        el.invCustPhone.textContent = order.customer.phone;
        el.invCustEmail.textContent = order.customer.email;
        el.invPaymentMethod.textContent = order.payment_method;

        el.invItemsBody.innerHTML = order.items.map(item => `
            <tr>
                <td>${escapeHtml(item.name)}</td>
                <td>₹${item.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td>${item.quantity}</td>
                <td class="text-right">₹${item.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
            </tr>
        `).join('');

        el.invSubtotal.textContent = `₹${order.subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        if (order.discount > 0) {
            el.invDiscountRow.classList.remove('hidden');
            el.invDiscount.textContent = `-₹${order.discount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
        } else {
            el.invDiscountRow.classList.add('hidden');
        }

        el.invDelivery.textContent = order.delivery_fee === 0 ? 'FREE' : `₹${order.delivery_fee.toFixed(2)}`;
        el.invGrandTotal.textContent = `₹${order.total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    };

    el.invoiceContinueBtn.addEventListener('click', () => {
        el.invoiceModal.classList.add('hidden');
    });

    // Helper: Escape HTML strings to prevent XSS
    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/[&<>'"]/g, tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag));
    }

    // Initial Bootstrap — read URL query params for category deep-links (from banners)
    const urlParams = new URLSearchParams(window.location.search);
    const urlCategory = urlParams.get('category');
    if (urlCategory) {
        state.currentCategory = urlCategory;
        el.categoryPills.forEach(pill => {
            pill.classList.toggle('active', pill.getAttribute('data-category') === urlCategory);
        });
        // Scroll past the banners to the product grid
        setTimeout(() => window.scrollTo({ top: 200, behavior: 'smooth' }), 300);
    }

    checkAuthStatus();
    if (state.currentCategory !== 'All' || state.searchQuery) {
        fetchProducts();
    } else {
        renderCatalog();
    }
    syncCartWithServer();
});
