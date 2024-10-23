import logging
import os
import asyncio
import aiofiles
import pickle

class Banlist:
	def __init__(self, path: str = "banlist/banned"):
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.setLevel(logging.DEBUG)

		self.path = os.path.join(*path.split("/"))
		
		# Create handlers if they aren't already set up
		if not self.logger.hasHandlers():
			console_handler = logging.StreamHandler()
			console_handler.setLevel(logging.DEBUG)
			file_handler = logging.FileHandler('Banlist.log')
			file_handler.setLevel(logging.DEBUG)
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			console_handler.setFormatter(formatter)
			file_handler.setFormatter(formatter)
			self.logger.addHandler(console_handler)
			self.logger.addHandler(file_handler)

		self.logger.debug("Initialised Banlist instance")

	async def check_list(self, ident: str) -> bool:
		if ident == "":
			self.logger.warning("Ident cannot be empty string")
			raise ValueError("Ident cannot be an empty string")

		try:
			async with aiofiles.open(self.path, 'rb') as f:
				ban_list_bin = await f.read()
				ban_list = pickle.loads(ban_list_bin)
		except FileNotFoundError:
			self.logger.warning(f"File not found: {self.path}")
			return False
		except pickle.UnpicklingError as e:
			self.logger.error(f"Failed to unpickle ban list: {e}")
			raise e

		return ident in ban_list

	async def ban(self, ident: str):
		if ident == "":
			self.logger.warning("Ident cannot be empty string")
			raise ValueError("Ident cannot be an empty string")

		try:
			async with aiofiles.open(self.path, 'rb') as f:
				ban_list_bin = await f.read()
				ban_list = pickle.loads(ban_list_bin)
		except FileNotFoundError:
			self.logger.debug(f"File not found: {self.path}. Initialising a new one")
			ban_list = set()
		except pickle.UnpicklingError as e:
			self.logger.error(f"Failed to unpickle ban list: {e}")
			raise e

		ban_list.add(ident)

		try:
			async with aiofiles.open(self.path, 'wb') as f:
				await f.write(pickle.dumps(ban_list))
				self.logger.debug(f"Successfully added {ident} to banlist {self.path}")
		except Exception as e:  # Generic catch for rare issues with writing/pickling
			self.logger.error("Failed to pickle while adding an ident")
			raise e

	async def unban(self, ident: str):
		if ident == "":
			self.logger.warning("Ident cannot be empty string")
			raise ValueError("Ident cannot be an empty string")

		try:
			async with aiofiles.open(self.path, 'rb') as f:
				ban_list_bin = await f.read()
				ban_list = pickle.loads(ban_list_bin)
		except FileNotFoundError:
			self.logger.debug(f"File not found: {self.path}. Initialising a new one")
			ban_list = set()
		except pickle.UnpicklingError as e:
			self.logger.error(f"Failed to unpickle ban list: {e}")
			raise e

		try:
			ban_list.remove(ident)
		except KeyError as e:
			self.logger.debug(f"{ident} not found in {self.path}")
			return

		try:
			async with aiofiles.open(self.path, 'wb') as f:
				await f.write(pickle.dumps(ban_list))
				self.logger.debug(f"Successfully removed {ident} from banlist {self.path}")
		except Exception as e:
			self.logger.error("Failed to pickle while adding an ident")
			raise e

async def main():
	banlist = Banlist()

if __name__ == '__main__':
	asyncio.run(main())