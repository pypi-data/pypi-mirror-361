Basic Usage
===========

Logging
-------

The `emrpy.logging` module provides safe, high-level logging utilities for both scripts and notebooks.

Setup is simple and safe — no root logger mutation, no duplicated handlers.

**In a script:**

.. code-block:: python

   from emrpy.logging import configure, get_logger

   # One-time global setup: file + console logging
   configure(
       level="INFO",
       log_dir="logs",
       filename="binance_dl.log",
       rotate_bytes=2 * 1024 * 1024,  # 2 MB rotation
       backups=1,
   )

   log = get_logger(__name__)
   log.info("This is information …")

**In a Jupyter notebook:**

.. code-block:: python

   from emrpy.logging import configure, get_logger

   # Console-only output (no file writes)
   configure(level="INFO", rotate_bytes=0, backups=0)

   log = get_logger(__name__)
   log.info("Notebook cell executed ✔")

Telegram Trading Bot
--------------------

The `telegrambot` module provides a lightweight, async-first interface to send trading notifications via Telegram. It's optimized for fast alerts, bulk messaging, and formatted trade summaries.

To use the bot, set your credentials as environment variables (optionally via a `.env` file):

.. code-block:: text

   # .env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here

**Send a simple message:**

.. code-block:: python

   import os
   import asyncio
   from dotenv import load_dotenv
   from emrpy import TelegramTradingBot

   load_dotenv()  # Load variables from .env

   bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
   chat_id = os.getenv("TELEGRAM_CHAT_ID")

   bot = TelegramTradingBot(bot_token=bot_token, chat_id=chat_id)

   async def main():
       await bot.send_message("Bot is now live 🚀")

   asyncio.run(main())

**Send a trade alert:**

.. code-block:: python

   import os
   import asyncio
   from dotenv import load_dotenv
   from emrpy import TelegramTradingBot

   load_dotenv()

   bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
   chat_id = os.getenv("TELEGRAM_CHAT_ID")

   bot = TelegramTradingBot(bot_token=bot_token, chat_id=chat_id)

   async def main():
       await bot.send_trade_alert(
           symbol="ETHUSD",
           action="BUY",
           price=1820.50,
           quantity=1.2,
           profit_loss=45.75
       )

   asyncio.run(main())

Decorators
----------

The `emrpy.decorators` module provides utilities for measuring execution time and memory usage of functions.

Use `@timer` for simple timing, or `@timer_and_memory` to also capture peak memory usage during execution.

**Measure function time:**

.. code-block:: python

   from emrpy.decorators import timer

   @timer
   def slow_function():
       sum([i for i in range(10_000_000)])

   slow_function()  # → prints execution time

**Measure time and memory:**

.. code-block:: python

   from emrpy.decorators import timer_and_memory

   @timer_and_memory
   def memory_intensive_function():
       return [i ** 2 for i in range(5_000_000)]

   memory_intensive_function()  # → prints time and peak memory usage
