# Reloadify 🚀

Welcome to **Reloadify**! A super-fast, feather-light Python tool that automatically reloads your HTML, CSS, and JavaScript files in the browser while you code. Say goodbye to manual refreshing! 👋

## 🌟 Features

-   **⚡ Blazing Fast:** Built for speed and efficiency.
-   **🤏 Ultra-Lightweight:** No heavy dependencies, just pure performance.
-   **🔄 Live Reloading:** Instantly see your changes in the browser.
-   **🛠️ Customizable:** Easily configure the file, directory, and port.

## 📦 Installation

Getting started is as easy as pie! Just open your terminal and run:

```bash
pip install reloadify
```

## 🚀 Usage

Once installed, navigate to your project's folder and let the magic happen!

```bash
reloadify [FILE]
```

-   `[FILE]` (optional): This is your main HTML file. If you don't specify one, `reloadify` will look for `index.html` in your current folder. It will automagically watch for changes in the same directory.

### ⚙️ Options

You can customize `reloadify` to fit your needs:

-   `-d, --directory <PATH>`: Tell `reloadify` which specific folder to watch for changes.

    *Example:*
    ```bash
    # Watch the 'src' folder for changes
    reloadify -d ./src
    ```

-   `-p, --port <PORT>`: Choose a custom port to run the server on. The default is `4005`.

    *Example:*
    ```bash
    # Run on port 8000
    reloadify -p 8000
    ```

### ✨ Examples

Here are a few ways you can use `reloadify`:

-   **Serve `index.html` and watch its folder (the default way):**
    ```bash
    reloadify
    ```

-   **Serve a specific HTML file and watch its folder:**
    ```bash
    reloadify my_app/index.html
    ```

-   **Serve `index.html` but watch a different folder for changes:**
    ```bash
    reloadify index.html -d ./src
    ```

-   **Serve `index.html` on a different port:**
    ```bash
    reloadify -p 8080
    ```

## 🌐 Connect with Me!

-   **Discord:** `lousybook01` 💬
-   **GitHub:** [LousyBook94](https://github.com/LousyBook94/) 🐙
-   **YouTube:** [@LousyBook01](http://youtube.com/@LousyBook01) 📺


## 📝 License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for details.

---

*Made with ❤️ by LousyBook & Gemini.*
