# Microsoft Account Checker

Lightweight tool to check Microsoft credentials, fetch Minecraft profiles, Hypixel stats, DonutSMP stats, and Bing Rewards points.

## Features

- Microsoft login via legacy RPS flow (no OAuth `msauth://` errors)
- Minecraft profile retrieval (username, UUID, capes)
- Game Pass detection (Normal, Game Pass PC, Game Pass Ultimate)
- Hypixel stats via official API (rank, level, bedwars stars, skyblock coins, first/last login)
- DonutSMP stats via official API (requires in‑game `/api` key)
- Bing Rewards points checker
- Sorted results in timestamped folders

## File Structure

```

.
├── main.py
├── donut_checker.py
├── minecraft.py
├── hypixel_checker.py
├── rewardpoints.py
├── acc.txt
├── hypixel_api_key.txt   (optional)
├── donut_api_key.txt     (optional)
├── requirements.txt
└── results/
└── YYYY-MM-DD_HHMMSS/
├── Hits.txt
├── Invalid.txt
├── 2FA.txt
├── NoMinecraft.txt
├── hypixel_stats.txt
├── donut_stats.txt
└── reward_points.txt

```

## Requirements

- Python 3.7+
- Install:
  ```bash
  pip install -r requirements.txt
```

Setup

1. Create acc.txt with email:password per line.
2. (Optional) Get Hypixel API key from developer.hypixel.net → paste into hypixel_api_key.txt
3. (Optional) Get DonutSMP API key: join DonutSMP server, type /api → paste into donut_api_key.txt
4. Run:
   ```bash
   python main.py
   ```

Output Files

· Hits.txt – accounts with Minecraft profile
· Invalid.txt – wrong credentials
· 2FA.txt – two‑factor authentication required
· NoMinecraft.txt – valid Microsoft account without Minecraft
· hypixel_stats.txt – Hypixel stats for each username
· donut_stats.txt – DonutSMP stats (if API key provided)
· reward_points.txt – Bing Rewards balance

Notes

· Sequential checking (no threading)
· No proxy support
· No Discord webhook
· No inbox scanning or payment method detection

Disclaimer

For educational purposes only.
