# Part(1)--------------------------------------------------------------------------------
# Part(2)--------------------------------------------------------------------------------
# Part(3)--------------------------------------------------------------------------------
# Part(4)--------------------------------------------------------------------------------   

    def update_smart_alerts(self, temp):
        """Generate alerts based on current conditions."""
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        alerts = []
        if temp > 26:
            alerts.append("Temperature is high - consider closing windows or lowering thermostat.")
        elif temp < 19:
            alerts.append("Temperature is low - consider raising thermostat or checking heating.")

        if not alerts:
            alerts.append("No alerts. All systems are normal.")

        for alert in alerts:
            tk.Label(self.alerts_frame, text=alert, font=("Arial", 10), bg=self.bg_color, fg="red").pack(anchor="w")

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.configure_style()
        self.toggle_button.config(text="Switch to Light Mode" if self.is_dark_mode else "Switch to Dark Mode",
                                  bg=self.bg_color, fg=self.fg_color)

    def configure_style(self):
        """Configure colors and styles based on the theme."""
        if self.is_dark_mode:
            self.bg_color = "#2E2E2E"
            self.fg_color = "#FFFFFF"
        else:
            self.bg_color = "#FFFFFF"
            self.fg_color = "#000000"

        self.config(bg=self.bg_color)
        for widget in self.winfo_children():
            widget.config(bg=self.bg_color, fg=self.fg_color)


# Run the app
if __name__ == "__main__":
    app = SmartHomeApp()
    app.mainloop()
