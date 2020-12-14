import requests
from bs4 import BeautifulSoup, element
import os
import sys


if __name__ == "__main__":
	print("for books from https://erenow.net/")
	try:
		book_url = sys.argv[1]
	except IndexError:
		book_url = input("Book-URL: ")

	main_soup = BeautifulSoup(requests.get(book_url).text, 'html.parser')
	book_title = "".join(x for x in main_soup.select_one("h1").text if x.isalnum() or x in(" ", "-"))
	print(f"{book_title=}")
	book_path = f"{os.getcwd()}/{book_title}"
	if not os.path.exists(book_path):
		os.makedirs(book_path)

	# write chapters
	chapter_elems = main_soup.select("#text-center p a[href]")
	for chapter_elem in chapter_elems:

		chapter_name = "".join(x for x in chapter_elem.text if x.isalnum() or x in(" ", "-"))
		chapter_url = f"{book_url}/{chapter_elem.attrs['href'].split('/')[-1]}"

		soup = BeautifulSoup(requests.get(chapter_url).text, 'html.parser')

		# clean up html
		del_elems_css = ("div.nk-share-place", "header", "div#nk-nav-mobile", 
			"footer", "div.nk-main div.nk-box", "#text-center div", "div.nk-search")
		for elem_css in del_elems_css:
			try:
				for elem in soup.select(elem_css):
					elem.decompose()
			except AttributeError:
				pass
		for elem in soup.select("div.row>div")[1:]:
			elem.decompose()

		# add image urls
		imgs = soup.select("div#text-center img")
		for img in imgs:
			img.attrs['src'] = f"{book_url}/{img.attrs['src']}"

		# dark mode
		if "--dark" in sys.argv:
			soup.select_one("body").attrs["style"] = "background-color: black; color: white;"

		# write file
		print(f"writing {chapter_name}...")
		with open(f"{book_path}/{chapter_name}.html", "w+", encoding="utf8") as f:
			f.write(str(soup))

	# write index file
	idx_soup = main_soup.select_one('#text-center')
	for link in idx_soup.select("a[href]"):
		link.attrs = {}
	with open(f"{book_path}/Index_Info.html", "w+", encoding="utf8") as f:
		f.write(str(idx_soup))