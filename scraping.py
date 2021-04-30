from bs4 import BeautifulSoup
import re

html = """<span data-testid="restaurant-menu-item"><div class="s-card-wrapper s-card-wrapper--fullCTA menuItemNew menuItem-inner u-flex" data-testid="menu-item" id="menuItem-2760456136"><div class="u-inset-squished-3 menuItemNew-details u-flex-reset-flexible has-right-spacing"><div class="u-flex"><div class="menuItemNew-name" data-testid="menu-item-name-container"><a class="menuItem-name u-block h6 s-link u-stack-x-2 s-card-title--addColor s-card-title--darkLink u-text-ellipsis" href="javascript:void(0)" title="De Camerón (Shrimp Fajita)">De Camerón (Shrimp Fajita)</a></div><span class="menuItem-badges u-flex-center-center"></span></div><div class="u-stack-y-2"><p class="u-text-secondary menuItemNew-description--truncate" data-testid="description">Shrimp Fajitas served with flour tortillas, guacamole, crema fresca, pico de gallo, pickled jalapeños, Mexican rice, and refried beans.</p></div><div></div></div><div class="menuItemNew-price u-rounded--large s-textBox"><span class="r2p"><cb-icon class="menuItem-loading" style=""><svg aria-hidden="true" class="cb-icon cb-icon-svg cb-icon--sm"><use xlink:href="#clock-back"></use></svg></cb-icon></span><span class="menuItem-priceAmount h6 s-textBox-title"><span><span class="menuItem-displayPrice" data-testid="menu-item-price" itemprop="price">$24.00</span></span></span></div></div></span>"""
soup = BeautifulSoup(html)
#print(soup.prettify())
title = soup.find_all(title = True)
if title:
    print(title[0]['title'])
price = soup.find('span',class_='menuItem-displayPrice')
if price:
    print(price.text)
# description = soup.find_all('p',{'data-testid':re.compile('.*description.*')})
# print(description)
description = soup.find_all(attrs={"data-testid":"description"})
if description:
    print(description[0].get_text())