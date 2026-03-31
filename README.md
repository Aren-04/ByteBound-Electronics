# ⚡ ByteBound Electronics 
**Premium Hardware Store & AI-Driven Shopping Experience**

ByteBound is a modern e-commerce platform designed for tech enthusiasts. It features a dynamic product catalog, a custom administrative seeding system, and an intelligent, empathetic chatbot assistant.

---

## 🚀 Key Features

* **Smart Inventory:** Real-time data synchronization using the **DummyJSON API**.
* **ByteBot AI:** An authentic, witty assistant powered by **Llama 3.1 (via Groq SDK)**. It understands product details, handles emotions, and provides straight-to-the-point tech advice.
* **Seamless Shopping:** Fully functional cart system and category-based navigation (Laptops, Smartphones, Accessories, Monitors).
* **Admin Dashboard:** Dedicated suite for system administrators to manage orders and trigger database seeding.
* **CI/CD Pipeline:** Automated testing and linting via **GitHub Actions** to ensure code reliability with every push.

---

## 🛠️ Technical Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python / Flask |
| **Database** | MongoDB (NoSQL) |
| **AI / LLM** | Groq Cloud (Llama-3.1-8b-instant) |
| **DevOps** | GitHub Actions, Docker, Docker Compose |
| **Frontend** | Jinja2, Bootstrap 5, HTML5/CSS3 |

---

## ⚙️ Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Aren-04/ByteBound-Electronics.git](https://github.com/Aren-04/ByteBound-Electronics.git)
    cd ByteBound-Electronics
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_api_key_here
    MONGO_URI=mongodb://localhost:27018/fynode_store
    SECRET_KEY=your_flask_secret_key
    ```

4.  **Run the Application:**
    ```bash
    python app.py
    ```

---

## 🤖 ByteBot Persona
ByteBot isn't your average "robotic" assistant. It was designed to be:
* **Supportive & Grounded:** Validates user feelings while providing technical accuracy.
* **Witty:** A touch of humor to make the shopping experience less clinical.
* **Knowledgeable:** Directly references the MongoDB product collection for real-time price and spec queries.

---

## 📈 Future Roadmap
- [ ] Integration with a live payment gateway (Stripe/Razorpay).
- [ ] User profile images and order history tracking.
- [ ] Cloud deployment via Render/Railway with MongoDB Atlas.

---
**Developed by [Aren](https://github.com/Aren-04)** *Student & Backend Developer*
