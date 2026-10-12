#!/usr/bin/env python3
"""
Automated Browsing Data & Cookie Cleaner for Google Flow CDP Profiles.
Implements Playbook [ERR-20261010-07]:
- Clears cookies, cache storage, local storage and service workers for https://flow.google.com/
- Clears browsing data from the last 7 days to eliminate PUBLIC_ERROR_UNUSUAL_ACTIVITY flags
- Reloads the Flow session cleanly.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def clean_profile_via_cdp(port: int) -> bool:
    print(f"[*] Connecting to Chrome on port {port} via CDP to clear Flow browsing data...")
    node_script = f"""
    import('playwright').then(async ({{chromium}}) => {{
      try {{
        const browser = await chromium.connectOverCDP('http://127.0.0.1:{port}');
        const context = browser.contexts()[0];
        if (!context) throw new Error('No browser context found');
        const page = context.pages()[0] || await context.newPage();
        
        const cdp = await context.newCDPSession(page);
        
        // 1. Clear storage & cookies specifically for Flow origin
        console.log('Clearing storage for origin https://flow.google.com/ ...');
        await cdp.send('Storage.clearDataForOrigin', {{
          origin: 'https://flow.google.com',
          storageTypes: 'cookies,storage,cache_storage,service_workers'
        }});
        
        // 2. Clear browser cache
        console.log('Clearing browser cache...');
        await cdp.send('Network.clearBrowserCache');
        
        // 3. Reload Flow page cleanly
        console.log('Reloading https://flow.google.com/ ...');
        await page.goto('https://flow.google.com/', {{waitUntil: 'domcontentloaded', timeout: 30000}});
        await page.waitForTimeout(2000);
        
        console.log('SUCCESS: Flow browsing data cleaned on port {port}. Current URL:', page.url());
        await browser.close();
        process.exit(0);
      }} catch (err) {{
        console.error('ERROR on port {port}:', err.message);
        process.exit(1);
      }}
    }});
    """
    cmd = ["node", "--input-type=module", "-e", node_script]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Clear Flow browsing data & 7-day cookies across CDP profiles")
    parser.add_argument("--port", type=int, choices=[9222, 9223, 9224], help="Target specific port (default: all 3)")
    args = parser.parse_args()

    ports = [args.port] if args.port else [9222, 9223, 9224]
    all_ok = True
    for p in ports:
        ok = clean_profile_via_cdp(p)
        if not ok:
            all_ok = False
        time.sleep(1)

    if all_ok:
        print("\n[✓] All target profiles successfully cleaned of abnormal Flow activity cookies!")
    else:
        print("\n[!] Warning: One or more profiles failed to clean. Check logs above.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
