// app.js
const API = "http://127.0.0.1:8000/api/products/";
const TOKEN = "Token YOUR_TOKEN_HERE"; // 👈 Put your real token here

// 1. Function to show products
async function showProducts() {
    const res = await fetch(API, { headers: { "Authorization": TOKEN } });
    const data = await res.json();
    
    // Build the list as one big string of HTML
    document.getElementById('container').innerHTML = data.map(p => `
        <div style="border:1px solid #555; padding:10px; margin-top:10px">
            <h3>${p.name}</h3>
            <p>Price: <b>KSh ${p.current_price}</b></p>
            <button onclick="deleteItem(${p.id})">Remove</button>
        </div>
    `).join('');
}

// 2. Function to add product
async function addItem() {
    const link = document.getElementById('urlInput').value;
    await fetch(API, {
        method: 'POST',
        headers: { "Authorization": TOKEN, "Content-Type": "application/json" },
        body: JSON.stringify({ jumia_url: link })
    });
    showProducts(); // Refresh the list
}

// 3. Function to delete product
async function deleteItem(id) {
    await fetch(API + id + "/", { 
        method: 'DELETE', 
        headers: { "Authorization": TOKEN } 
    });
    showProducts(); // Refresh the list
}

// Run this as soon as the page loads
showProducts();