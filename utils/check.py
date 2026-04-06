import traceback
import httpx


class ServiceChecker:
    FUTURISTIC_LOGO = "🤖"

    async def run_check(self, name: str, url: str, path: list[str]):
        if not url or not url.strip():
            return f"⚠️ *{name}* has no endpoint configured."

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                try:
                    res_data = response.json()

                except Exception:
                    res_data = response.text

                return self.format_response(name, res_data, path)

        except Exception as e:
            return f"❌ *Error:* `{str(e)}`"

    def format_response(self, name: str, data, path: list[str]):
        try:
            header = f"{self.FUTURISTIC_LOGO} *{name}*  |  {' > '.join(path)}\n\n"

            if not isinstance(data, dict):
                return header + f"❌ *Invalid Response*\n`{str(data)[:500]}`"

            status = data.get("status", "Unknown")
            message = data.get("message", "No message")
            code = data.get("status_code", "N/A")
            latency = data.get("latency_sec")

            status_icon = (
                "🟢 ONLINE" if code == 200 else
                "🟡 UNKNOWN" if code == "N/A" else
                "🔴 OFFLINE"
            )

            if latency is not None:
                latency_label = (
                    "⚡ FAST" if latency < 0.3 else
                    "🚀 NORMAL" if latency < 0.7 else
                    "🐢 SLOW"
                )
            else:
                latency_label = "N/A"

            summary = (
                f"━━━━━━━━━━━━━━━\n"
                f"{status_icon} | Status: `{status}`\n"
                f"🧾 | Code: `{code}`\n"
                f"💬 | Message: {message}\n"
                f"⏱️ | Latency: `{latency}` sec ({latency_label})\n"
                f"━━━━━━━━━━━━━━━"
            )
            return header + summary

        except Exception:
            traceback.print_exc()
            return f"❌ Formatting error for {name}"
