config={
        'scrapers': {
            'guild_dreams': {
                'type': 'guild_dreams',
                'headless': True,
                'page_load_delay': 3,
                'categories': {
                    'magic': {
                        'url': 'https://www.guildreams.com/collection/magic-the-gathering?order=id&way=DESC&limit=106&page=1',
                        'selectors': {
                            'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                            'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                            'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                            'stock_selector': '//div[@data-bs="product.stock"]',
                            'description_selector': '//section[@id="bs-product-description"]',
                            'title_selector': '//article/h2',
                        }
                    },
                    "yugioh":{
                        'url': 'https://www.guildreams.com/collection/yu-gi-oh?order=id&way=DESC&limit=130&page=1',
                        'selectors': {
                            'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                            'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                            'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                            'stock_selector': '//div[@data-bs="product.stock"]',
                            'description_selector': '//section[@id="bs-product-description"]',
                            'title_selector': '//article/h2',
                        }
                    },
                    "pokemon":{
                        'url': 'https://www.guildreams.com/collection/pokemon?order=id&way=DESC&limit=167&page=1',
                        'selectors': {
                            'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                            'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                            'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                            'stock_selector': '//div[@data-bs="product.stock"]',
                            'description_selector': '//section[@id="bs-product-description"]',
                            'title_selector': '//article/h2',
                            }
                    }
                }
            }
        }
    }

scrapers_config = {
    'scrapers': {
        'guild_dreams': {
            'type': 'guild_dreams',
            'headless': True,
            'page_load_delay': 3,
            'categories': {
                'magic': {
                    'url': 'https://www.guildreams.com/collection/magic-the-gathering?order=id&way=DESC&limit=106&page=1',
                    'selectors': {
                        'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                        'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                        'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                        'stock_selector': '//div[@data-bs="product.stock"]',
                        'description_selector': '//section[@id="bs-product-description"]',
                        'title_selector': '//article/h2',
                    }
                },
                'yugioh': {
                    'url': 'https://www.guildreams.com/collection/yu-gi-oh?order=id&way=DESC&limit=130&page=1',
                    'selectors': {
                        'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                        'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                        'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                        'stock_selector': '//div[@data-bs="product.stock"]',
                        'description_selector': '//section[@id="bs-product-description"]',
                        'title_selector': '//article/h2',
                    }
                },
                'pokemon': {
                    'url': 'https://www.guildreams.com/collection/pokemon?order=id&way=DESC&limit=167&page=1',
                    'selectors': {
                        'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                        'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                        'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                        'stock_selector': '//div[@data-bs="product.stock"]',
                        'description_selector': '//section[@id="bs-product-description"]',
                        'title_selector': '//article/h2',
                    }
                }
            }
        },
        'card_universe': {
            'type': 'card_universe',
            'headless': True,
            'page_load_delay': 2,
            'categories': {
                'pokemon': {
                    'url': 'https://carduniverse.cl/collections/pokemon-tcg',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                },
                'yugioh': {
                    'url': 'https://carduniverse.cl/collections/yu-gi-oh',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                },
                'magic': {
                    'url': 'https://carduniverse.cl/collections/magic-the-gathering',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                }
            }
        },
        'huntercardtcg': {
            'type': 'huntercardtcg',
            'headless': True,
            'page_load_delay': 2,
            'categories': {
                'pokemon': {
                    'url': 'https://www.huntercardtcg.com/categoria-producto/pokemon-tcg/',
                    'selectors': {
                        'product_selector': "//ul[contains(@class, 'products')]/li",
                        'urls_selector': ".//a[contains(@class, 'woocommerce-LoopProduct-link')]",
                        'price_selector': ".//span[contains(@class, 'price')]",
                        'stock_selector': ".//span[contains(@class, 'stock')]",
                        'description_selector': "//div[@id='tab-description']",
                        'title_selector': "//h1[contains(@class, 'product_title')]"
                    }
                },
                'yugioh': {
                    'url': 'https://www.huntercardtcg.com/categoria-producto/yugioh/',
                    'selectors': {
                        'product_selector': "//ul[contains(@class, 'products')]/li",
                        'urls_selector': ".//a[contains(@class, 'woocommerce-LoopProduct-link')]",
                        'price_selector': ".//span[contains(@class, 'price')]",
                        'stock_selector': ".//span[contains(@class, 'stock')]",
                        'description_selector': "//div[@id='tab-description']",
                        'title_selector': "//h1[contains(@class, 'product_title')]"
                    }
                },
                'magic': {
                    'url': 'https://www.huntercardtcg.com/categoria-producto/magic-the-gathering/',
                    'selectors': {
                        'product_selector': "//ul[contains(@class, 'products')]/li",
                        'urls_selector': ".//a[contains(@class, 'woocommerce-LoopProduct-link')]",
                        'price_selector': ".//span[contains(@class, 'price')]",
                        'stock_selector': ".//span[contains(@class, 'stock')]",
                        'description_selector': "//div[@id='tab-description']",
                        'title_selector': "//h1[contains(@class, 'product_title')]"
                    }
                }
            }
        },
        'thirdimpact': {
            'type': 'thirdimpact',
            'headless': True,
            'page_load_delay': 2,
            'categories': {
                'pokemon': {
                    'url': 'https://www.thirdimpact.cl/collection/pokemon',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                },
                'yugioh': {
                    'url': 'https://www.thirdimpact.cl/collection/yu-gi-oh',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                },
                'magic': {
                    'url': 'https://www.thirdimpact.cl/collection/magic-the-gathering',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                }
            }
        }
    }
}
