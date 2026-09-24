"""
OTMB-Based 50 Famous South Indian Food Recipes
Target Platform: MicroPython on Raspberry Pi Pico (RP2040) / Desktop Python
Features: Compact OTMB records, fast index lookup, nutrition, dietary filters, step-by-step guides.
"""

import sys

# 50 Authentic South Indian Recipes Database
RECIPES_DB = [
    # --- KARNATAKA ---
    {
        "id": 1, "name": "Bisi Bele Bath", "region": "Karnataka", "diet": "Veg",
        "prep_min": 20, "cook_min": 25, "cal": 380,
        "ingredients": ["Rice", "Toor Dal", "Mixed Veggies", "Bisi Bele Bath Masala", "Tamarind", "Ghee", "Cashews"],
        "steps": "1. Cook rice and toor dal together until soft.\n2. Sauté veggies in ghee with mustard, curry leaves, and cashews.\n3. Add tamarind pulp, jaggery, bisi bele bath powder, and salt.\n4. Simmer for 10 min, finish with generous ghee drizzle."
    },
    {
        "id": 2, "name": "Mysore Masala Dosa", "region": "Karnataka", "diet": "Veg",
        "prep_min": 480, "cook_min": 10, "cal": 340,
        "ingredients": ["Fermented Dosa Batter", "Potato Masala", "Red Garlic Chutney", "Butter", "Curry Leaves"],
        "steps": "1. Heat cast iron tawa, spread ladle of batter.\n2. Smear red chilli-garlic chutney inside.\n3. Place spiced aloo sabzi in center with butter.\n4. Roast until crisp brown and fold."
    },
    {
        "id": 3, "name": "Ragi Mudde", "region": "Karnataka", "diet": "Vegan",
        "prep_min": 5, "cook_min": 15, "cal": 220,
        "ingredients": ["Ragi (Finger Millet) Flour", "Water", "Salt", "Ghee (optional)"],
        "steps": "1. Boil water with pinch of salt and a spoonful of ragi slurry.\n2. Add remaining ragi flour without stirring, let cook 3 min.\n3. Vigorously mix with mudde stick (kolu) into smooth dough.\n4. Shape into smooth balls with wet hands; serve with Bassaru or Soppina Saaru."
    },
    {
        "id": 4, "name": "Mysore Pak", "region": "Karnataka", "diet": "Veg",
        "prep_min": 10, "cook_min": 20, "cal": 450,
        "ingredients": ["Besan (Gram Flour)", "Desi Ghee", "Sugar", "Cardamom"],
        "steps": "1. Make sugar syrup of 1-string consistency.\n2. Sift besan and add slowly without lumps.\n3. Pour smoking hot ghee in continuous batches while stirring.\n4. Once porous and honeycombed, pour into tray and slice."
    },
    {
        "id": 5, "name": "Mangalore Buns", "region": "Karnataka", "diet": "Veg",
        "prep_min": 240, "cook_min": 15, "cal": 290,
        "ingredients": ["Overripe Bananas", "Maida / Atta", "Curd", "Cumin", "Sugar", "Oil for frying"],
        "steps": "1. Mash bananas with sugar, cumin, curd, and salt.\n2. Knead with flour into soft dough, rest 4 hours.\n3. Roll into thick puris and deep fry in hot oil until puffed golden.\n4. Serve with spicy coconut chutney."
    },
    {
        "id": 6, "name": "Neer Dosa", "region": "Karnataka", "diet": "Vegan",
        "prep_min": 180, "cook_min": 10, "cal": 180,
        "ingredients": ["Raw Rice (Sona Masoori)", "Grated Coconut", "Water", "Salt"],
        "steps": "1. Grind soaked rice and coconut to an ultra-watery, thin batter.\n2. Pour onto hot pan like water splash (no spreading needed).\n3. Cover and steam for 1 min.\n4. Fold into triangles; serve with coconut jaggery or chicken curry."
    },
    {
        "id": 7, "name": "Maddur Vada", "region": "Karnataka", "diet": "Veg",
        "prep_min": 15, "cook_min": 15, "cal": 280,
        "ingredients": ["Rice Flour", "Rava (Semolina)", "Maida", "Sliced Onions", "Green Chillies", "Curry Leaves", "Hot Oil"],
        "steps": "1. Mix flours, sliced onions, chillies, curry leaves, and salt.\n2. Pour 2 tbsp smoking hot oil into flour (moin) and knead into stiff dough.\n3. Flatten into thin patties on parchment paper.\n4. Deep fry on medium flame until crispy golden brown."
    },
    {
        "id": 8, "name": "Akki Roti", "region": "Karnataka", "diet": "Vegan",
        "prep_min": 10, "cook_min": 10, "cal": 210,
        "ingredients": ["Rice Flour", "Finely Chopped Onions", "Dill Leaves (Sabbasige)", "Green Chillies", "Cumin Seeds"],
        "steps": "1. Mix rice flour with onions, fresh dill leaves, chillies, cumin, and warm water.\n2. Pat dough directly onto a cool, oiled tawa or banana leaf.\n3. Make 3 small holes, drizzle oil, cook covered until crisp.\n4. Serve with Yennegayi (Stuffed Brinjal) or butter."
    },
    {
        "id": 9, "name": "Kundapura Chicken Kori Rotti", "region": "Karnataka", "diet": "Non-Veg",
        "prep_min": 20, "cook_min": 35, "cal": 420,
        "ingredients": ["Crisp Rice Wafers (Kori Rotti)", "Chicken", "Byadgi Chillies", "Coconut Milk", "Ghee", "Spices"],
        "steps": "1. Roast Byadgi chillies, coriander, cumin, garlic, and coconut into fine paste.\n2. Cook chicken in coconut masala gravy and thin with coconut milk.\n3. Crush crispy kori rottis on a plate.\n4. Pour boiling hot, spiced chicken gravy over rottis and enjoy instantly."
    },
    {
        "id": 10, "name": "Chitranna (Lemon Rice)", "region": "Karnataka", "diet": "Vegan",
        "prep_min": 5, "cook_min": 10, "cal": 250,
        "ingredients": ["Cooked Rice", "Fresh Lemon Juice", "Peanuts", "Mustard Seeds", "Curry Leaves", "Turmeric", "Green Chillies"],
        "steps": "1. Heat oil, temper mustard, urad dal, chana dal, peanuts, and green chillies.\n2. Add turmeric, curry leaves, and salt.\n3. Turn off heat, add lemon juice to tadka.\n4. Gently mix into cooled cooked rice."
    },
    {
        "id": 11, "name": "Vangi Bath", "region": "Karnataka", "diet": "Vegan",
        "prep_min": 15, "cook_min": 20, "cal": 310,
        "ingredients": ["Rice", "Green Brinjal (Eggplant)", "Vangi Bath Powder", "Tamarind", "Peanuts", "Curry Leaves"],
        "steps": "1. Sauté sliced brinjal in oil with mustard, peanuts, and turmeric.\n2. Add tamarind pulp, salt, and aromatic vangi bath masala powder.\n3. Cook until brinjal is tender and masala releases oil.\n4. Mix thoroughly with cooked rice."
    },
    {
        "id": 12, "name": "Dharwad Pedha", "region": "Karnataka", "diet": "Veg",
        "prep_min": 10, "cook_min": 45, "cal": 390,
        "ingredients": ["Dharwad Buffalo Milk Khoa", "Sugar", "Ghee", "Cardamom", "Powdered Sugar for dusting"],
        "steps": "1. Roast khoa in heavy kadai with ghee continuously on low flame.\n2. Keep browning until deep caramel brown color is reached.\n3. Add sugar, melt, and cook to rolling stage.\n4. Shape into rustic cylinders and roll in powdered castor sugar."
    },

    # --- TAMIL NADU ---
    {
        "id": 13, "name": "Classic Idli & Sambar", "region": "Tamil Nadu", "diet": "Vegan",
        "prep_min": 600, "cook_min": 12, "cal": 150,
        "ingredients": ["Idli Rice", "Urad Dal", "Fenugreek Seeds", "Drumsticks", "Shallots (Sambar Onions)", "Sambar Powder"],
        "steps": "1. Soak rice and dal, grind to smooth aerated batter, ferment 10 hours.\n2. Pour into greased idli molds and steam 10 min.\n3. Prepare sambar with toor dal, shallots, tamarind, and fresh sambar powder.\n4. Serve piping hot idlis floating in sambar."
    },
    {
        "id": 14, "name": "Medu Vada", "region": "Tamil Nadu", "diet": "Vegan",
        "prep_min": 180, "cook_min": 15, "cal": 260,
        "ingredients": ["Whole Black Urad Dal", "Black Peppercorns", "Curry Leaves", "Ginger", "Green Chillies", "Oil for frying"],
        "steps": "1. Grind soaked urad dal with minimal water into fluffy, aerated batter.\n2. Fold in crushed peppercorns, ginger, chillies, and curry leaves.\n3. Shape into doughnut rings on wet palm and slide into hot oil.\n4. Fry until ultra-crisp outside and pillowy inside."
    },
    {
        "id": 15, "name": "Ven Pongal", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 5, "cook_min": 20, "cal": 320,
        "ingredients": ["Raw Rice", "Yellow Moong Dal", "Black Pepper", "Cumin Seeds", "Ginger", "Cashews", "Desi Ghee"],
        "steps": "1. Roast moong dal lightly, pressure cook with rice until soft and mushy.\n2. In generous ghee, temper cumin, whole peppercorns, crushed ginger, curry leaves, and cashews.\n3. Pour sputtering tadka over rice-dal mixture with salt.\n4. Mix vigorously and serve steaming hot with coconut chutney."
    },
    {
        "id": 16, "name": "Chettinad Chicken Curry", "region": "Tamil Nadu", "diet": "Non-Veg",
        "prep_min": 20, "cook_min": 30, "cal": 440,
        "ingredients": ["Chicken", "Kalpasi (Stone Flower)", "Star Anise", "Marathi Moggu", "Shallots", "Fresh Coconut Paste", "Black Pepper"],
        "steps": "1. Dry roast whole Chettinad spices (kalpasi, star anise, pepper, fennel, coriander) and grind.\n2. Sauté shallots, curry leaves, and tomatoes in gingelly oil.\n3. Add chicken, ground masala, and coconut paste.\n4. Simmer until oil separates and chicken is succulent."
    },
    {
        "id": 17, "name": "Kothu Parotta", "region": "Tamil Nadu", "diet": "Non-Veg",
        "prep_min": 10, "cook_min": 15, "cal": 460,
        "ingredients": ["Layered Malabar/Madurai Parotta", "Eggs / Shredded Meat", "Salna (Spicy Gravy)", "Onions", "Green Chillies"],
        "steps": "1. Shred flaky parottas into bite-sized pieces.\n2. Sauté onions, chillies, and curry leaves on high-heat iron tawa.\n3. Add eggs/meat, shredded parotta, and ladle of rich salna gravy.\n4. Chop and beat vigorously with two metal spatulas in rhythmic clangs until blended."
    },
    {
        "id": 18, "name": "Filter Coffee (Degree Kaapi)", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 15, "cook_min": 5, "cal": 90,
        "ingredients": ["80:20 Coffee-Chicory Blend", "Boiling Water", "Full Cream Buffalo Milk", "Sugar"],
        "steps": "1. Add coffee powder to upper chamber of brass filter, press plunger, pour boiling water.\n2. Collect thick first-decoction (10 min).\n3. Boil fresh thick milk with sugar.\n4. Froth by stretching between davarah and tumbler from height."
    },
    {
        "id": 19, "name": "Milagu Rasam (Pepper Rasam)", "region": "Tamil Nadu", "diet": "Vegan",
        "prep_min": 5, "cook_min": 10, "cal": 70,
        "ingredients": ["Crushed Black Pepper", "Cumin", "Garlic", "Tomatoes", "Tamarind", "Curry Leaves", "Ghee"],
        "steps": "1. Coarsely crush black pepper, cumin, and unpeeled garlic cloves.\n2. Simmer tomato and tamarind water with turmeric, salt, and crushed spice mix.\n3. When it reaches a gentle single froth (do not boil!), temper with mustard and curry leaves.\n4. Garnish with coriander; ideal for cold/cough."
    },
    {
        "id": 20, "name": "Curd Rice (Thayir Sadam)", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 5, "cook_min": 10, "cal": 190,
        "ingredients": ["Overcooked Rice", "Fresh Homemade Curd", "Milk", "Mustard Seeds", "Ginger", "Green Chillies", "Pomegranate / Grapes"],
        "steps": "1. Mash warm cooked rice softly.\n2. Mix with fresh thick curd and a splash of milk to prevent souring.\n3. Temper mustard, urad dal, ginger, chillies, and asafoetida in oil.\n4. Fold into curd rice and top with pomegranate pearls."
    },
    {
        "id": 21, "name": "Kuzhi Paniyaram", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 10, "cook_min": 12, "cal": 210,
        "ingredients": ["Sour Dosa/Idli Batter", "Finely Chopped Onions", "Mustard", "Green Chillies", "Curry Leaves", "Oil"],
        "steps": "1. Temper onions, mustard, chillies, and curry leaves; mix into sour idli batter.\n2. Heat appe/paniyaram cast iron pan with a few drops of oil in each cavity.\n3. Fill cavities with batter, cook covered on medium heat.\n4. Flip with wooden skewer when bottom is golden; serve with Kara Chutney."
    },
    {
        "id": 22, "name": "Adai Avial", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 240, "cook_min": 15, "cal": 330,
        "ingredients": ["Mixed Dals (Chana, Toor, Urad)", "Rice", "Red Chillies", "Asafoetida", "Avial (Mixed Veggies in Coconut-Curd)"],
        "steps": "1. Soak rice and 3 lentils with dry red chillies; grind into coarse, thick batter.\n2. Spread thick pancake on tawa with center hole for oil.\n3. Roast both sides until crunchy.\n4. Serve hot with rich vegetable avial and a dollop of jaggery."
    },
    {
        "id": 23, "name": "Jigarthanda", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 10, "cook_min": 5, "cal": 320,
        "ingredients": ["Badam Pisin (Almond Gum)", "Nannari Syrup", "Condensed Basundi Milk", "Vanilla Ice Cream"],
        "steps": "1. Soak badam pisin overnight into jelly.\n2. In a tall glass, add 2 spoons soaked badam pisin and nannari syrup.\n3. Pour reduced, caramel-thickened basundi milk.\n4. Top with a scoop of traditional ice cream."
    },
    {
        "id": 24, "name": "Chettinad Mushroom Biryani", "region": "Tamil Nadu", "diet": "Veg",
        "prep_min": 20, "cook_min": 25, "cal": 370,
        "ingredients": ["Seeraga Samba Rice", "Button Mushrooms", "Chettinad Spices", "Mint", "Coriander", "Ghee", "Curd"],
        "steps": "1. Sauté whole spices in ghee; add onions, ginger-garlic paste, and green chillies.\n2. Add mushrooms, curd, mint, coriander, and biryani masala.\n3. Add washed Seeraga Samba short-grain rice and hot water (1:2 ratio).\n4. Seal pot and cook on low dum for 15 min."
    },

    # --- KERALA ---
    {
        "id": 25, "name": "Appam with Vegetable Stew", "region": "Kerala", "diet": "Vegan",
        "prep_min": 480, "cook_min": 15, "cal": 260,
        "ingredients": ["Raw Rice", "Fermented Toddy / Yeast", "Coconut Milk", "Potatoes", "Carrots", "Beans", "Whole Spices"],
        "steps": "1. Grind rice with coconut milk and ferment batter.\n2. Swirl batter in curved appachatti pan for lace borders and spongy center.\n3. Simmer veggies with whole cinnamon, cardamom, cloves, and ginger.\n4. Add thick first-press coconut milk and coconut oil finish."
    },
    {
        "id": 26, "name": "Kerala Puttu and Kadala Curry", "region": "Kerala", "diet": "Vegan",
        "prep_min": 480, "cook_min": 20, "cal": 350,
        "ingredients": ["Coarse Rice Flour", "Grated Fresh Coconut", "Black Chickpeas (Kadala)", "Roasted Coconut Masala", "Curry Leaves"],
        "steps": "1. Moisten rice flour with salted water to crumbly texture.\n2. Layer cylindrical puttu maker alternately with fresh coconut and flour; steam 5 min.\n3. Pressure cook soaked black chickpeas in spicy roasted coconut paste (Theeyal masala).\n4. Serve together for iconic breakfast."
    },
    {
        "id": 27, "name": "Kerala Sadya Avial", "region": "Kerala", "diet": "Veg",
        "prep_min": 20, "cook_min": 15, "cal": 180,
        "ingredients": ["Raw Banana", "Elephant Foot Yam (Chena)", "Drumstick", "Carrot", "Coconut-Cumin Paste", "Sour Curd", "Coconut Oil"],
        "steps": "1. Cut long batons of vegetables and cook with turmeric and salt until just tender.\n2. Grind coconut, cumin seeds, and green chillies into coarse paste.\n3. Fold paste and sour curd into cooked veggies on low flame.\n4. Pour raw cold-pressed coconut oil and fresh curry leaves over top."
    },
    {
        "id": 28, "name": "Malabar Fish Curry (Meen Curry)", "region": "Kerala", "diet": "Non-Veg",
        "prep_min": 15, "cook_min": 20, "cal": 360,
        "ingredients": ["Seer Fish / Kingfish", "Kudampuli (Malabar Tamarind)", "Shallots", "Kashmiri Red Chilli", "Fenugreek", "Coconut Oil"],
        "steps": "1. Soak smoked Kudampuli in warm water.\n2. In an earthenware pot (Meen Chatti), heat coconut oil; sauté shallots, ginger, garlic, and curry leaves.\n3. Add chilli powder, coriander powder, fenugreek, and kudampuli water.\n4. Slide in fish steaks and simmer until gravy thickens."
    },
    {
        "id": 29, "name": "Thalassery Biryani", "region": "Kerala", "diet": "Non-Veg",
        "prep_min": 30, "cook_min": 40, "cal": 490,
        "ingredients": ["Kaima / Jeerakasala Rice", "Chicken", "Malabar Garam Masala", "Fried Onions (Besta)", "Cashews", "Raisins", "Ghee"],
        "steps": "1. Marinate chicken in green chilli-mint paste and cook into rich masala base.\n2. Cook small-grain Kaima rice with whole spices and ghee to 90%.\n3. Layer chicken masala and rice alternately, sprinkle with fried onions, nuts, and saffron.\n4. Seal lid with dough for airtight slow dum."
    },
    {
        "id": 30, "name": "Pazham Pori (Banana Fritters)", "region": "Kerala", "diet": "Vegan",
        "prep_min": 10, "cook_min": 10, "cal": 230,
        "ingredients": ["Ripe Nendran Bananas", "All-Purpose Flour / Rice Flour", "Turmeric", "Sugar", "Coconut Oil"],
        "steps": "1. Slice ripe yellow Nendran bananas lengthwise.\n2. Make smooth dip batter with flour, pinch of turmeric, sugar, and water.\n3. Dip banana slices into batter evenly.\n4. Deep fry in pure coconut oil until golden and crispy."
    },
    {
        "id": 31, "name": "Palada Payasam (Pradhaman)", "region": "Kerala", "diet": "Veg",
        "prep_min": 10, "cook_min": 60, "cal": 380,
        "ingredients": ["Rice Ada (Flakes)", "Full Cream Milk", "Sugar", "Cardamom", "Ghee"],
        "steps": "1. Boil milk in heavy uruli; reduce on slow flame until light pink.\n2. Wash and add rice ada flakes directly to simmering reduced milk.\n3. Cook until ada is soft and translucent.\n4. Add sugar and cardamom; simmer to creamy perfection."
    },
    {
        "id": 32, "name": "Erissery (Pumpkin & Red Beans)", "region": "Kerala", "diet": "Vegan",
        "prep_min": 15, "cook_min": 20, "cal": 200,
        "ingredients": ["Yellow Pumpkin (Mathanga)", "Red Cowpeas (Vanpayar)", "Grated Coconut", "Cumin", "Turmeric", "Curry Leaves"],
        "steps": "1. Pressure cook pumpkin and soaked red cowpeas with turmeric and chilli.\n2. Mash lightly, add ground coconut-cumin paste, and simmer.\n3. In coconut oil, roast grated coconut with mustard and curry leaves until golden brown.\n4. Stir toasted aromatic coconut topping into curry."
    },
    {
        "id": 33, "name": "Kerala Beef Fry (Ularthiyathu)", "region": "Kerala", "diet": "Non-Veg",
        "prep_min": 20, "cook_min": 35, "cal": 410,
        "ingredients": ["Meat Cuts", "Coconut Slivers (Thenga Kothu)", "Fennel Seeds", "Black Pepper", "Garlic", "Shallots", "Curry Leaves"],
        "steps": "1. Pressure cook meat with turmeric, chilli, coriander, pepper, and garam masala.\n2. In cast iron pan, heat coconut oil; fry coconut slivers until reddish brown.\n3. Sauté crushed shallots, ginger, garlic, and curry leaves.\n4. Add cooked meat and slow-roast on low flame until dark brown and aromatic."
    },
    {
        "id": 34, "name": "Olan (Ash Gourd in Coconut Milk)", "region": "Kerala", "diet": "Vegan",
        "prep_min": 10, "cook_min": 15, "cal": 140,
        "ingredients": ["Ash Gourd (Kumbalanga)", "Red Cowpeas", "Green Chillies", "Thin & Thick Coconut Milk", "Coconut Oil"],
        "steps": "1. Cook ash gourd and red cowpeas with green chillies in thin coconut milk.\n2. Once tender, pour rich first-extract thick coconut milk.\n3. Warm through gently without boiling.\n4. Turn off heat and drizzle fresh coconut oil with curry leaves."
    },
    {
        "id": 35, "name": "Kerala Egg Roast (Mutta Roast)", "region": "Kerala", "diet": "Non-Veg",
        "prep_min": 10, "cook_min": 20, "cal": 280,
        "ingredients": ["Hard Boiled Eggs", "Sliced Onions", "Tomatoes", "Ginger-Garlic", "Meat Masala", "Curry Leaves", "Coconut Oil"],
        "steps": "1. Make slits in boiled eggs and sear lightly in spiced oil.\n2. Caramelize abundant sliced onions in coconut oil until translucent brown.\n3. Add tomatoes, spices, and curry leaves to create thick masala glaze.\n4. Toss eggs into thick masala; serve with Appam or Parotta."
    },

    # --- ANDHRA PRADESH & TELANGANA ---
    {
        "id": 36, "name": "Hyderabadi Dum Biryani", "region": "Telangana", "diet": "Non-Veg",
        "prep_min": 60, "cook_min": 45, "cal": 520,
        "ingredients": ["Basmati Rice", "Mutton / Chicken", "Fried Onions (Birista)", "Mint", "Saffron Milk", "Ghee", "Potli Spices"],
        "steps": "1. Marinate meat with raw papaya, yoghurt, ginger-garlic, mint, and whole spices for 4 hrs.\n2. Cook long-grain Basmati rice to 70% in whole spice broth.\n3. Layer raw marinated meat at bottom (Kacchi Biryani), top with rice, fried onions, saffron ghee.\n4. Seal heavy handi with dough; cook on high for 15 min, then slow coal dum for 30 min."
    },
    {
        "id": 37, "name": "Andhra Pesarattu", "region": "Andhra Pradesh", "diet": "Vegan",
        "prep_min": 240, "cook_min": 10, "cal": 210,
        "ingredients": ["Whole Green Gram (Moong)", "Ginger", "Green Chillies", "Cumin Seeds", "Chopped Onions (Upma filling)"],
        "steps": "1. Grind soaked green gram with ginger, green chillies, and cumin (no fermentation needed).\n2. Pour thin batter on smoking hot griddle.\n3. Top with finely chopped onions, cumin, or a dollop of Upma (MLA Pesarattu).\n4. Roast crisp with oil; serve with Allam Pachadi (Ginger Chutney)."
    },
    {
        "id": 38, "name": "Gongura Mutton", "region": "Andhra Pradesh", "diet": "Non-Veg",
        "prep_min": 20, "cook_min": 40, "cal": 480,
        "ingredients": ["Tender Mutton", "Fresh Gongura (Sorrel) Leaves", "Guntur Red Chillies", "Coriander", "Garlic", "Onions"],
        "steps": "1. Sauté gongura leaves in oil until soft and mushy; mash to paste.\n2. Pressure cook mutton with onions, ginger-garlic, and fiery Guntur chilli powder.\n3. Combine cooked mutton gravy with tangy gongura paste.\n4. Simmer for 10 min for flavors to marry; serve with hot steamed rice and ghee."
    },
    {
        "id": 39, "name": "Gongura Pachadi", "region": "Andhra Pradesh", "diet": "Vegan",
        "prep_min": 10, "cook_min": 10, "cal": 110,
        "ingredients": ["Red Stem Gongura Leaves", "Guntur Dry Red Chillies", "Fenugreek Seeds", "Coriander Seeds", "Garlic", "Sesame Oil"],
        "steps": "1. Roast dry red chillies, coriander seeds, and fenugreek in oil; powder coarsely.\n2. Sauté gongura leaves until wilted and cooked.\n3. Pound gongura, spice powder, garlic, and salt in stone pestle.\n4. Temper with mustard and garlic in sesame oil; legendary Andhra staple."
    },
    {
        "id": 40, "name": "Andhra Natu Kodi Pulusu", "region": "Andhra Pradesh", "diet": "Non-Veg",
        "prep_min": 20, "cook_min": 45, "cal": 450,
        "ingredients": ["Country Chicken (Natu Kodi)", "Poppy Seeds Paste (Gasa Gasalu)", "Guntur Chilli Powder", "Tamarind", "Coriander"],
        "steps": "1. Sauté country chicken in gingelly oil with onions, turmeric, and ginger-garlic.\n2. Add fiery chilli powder, coriander powder, and poppy seeds-coconut paste.\n3. Add tamarind water and pressure cook for 5-6 whistles until meat is tender.\n4. Serve piping hot with Ragi Sankati or Garelu."
    },
    {
        "id": 41, "name": "Ulava Charu (Horsegram Soup)", "region": "Andhra Pradesh", "diet": "Veg",
        "prep_min": 480, "cook_min": 60, "cal": 160,
        "ingredients": ["Horsegram (Ulavalu)", "Tamarind", "Ghee", "Mustard", "Cumin", "Garlic", "Curry Leaves"],
        "steps": "1. Slow-boil horsegram in plenty of water for 2-3 hours to extract dark, rich broth.\n2. Reduce broth by simmering with tamarind extract, salt, and crushed pepper-cumin.\n3. Temper generously with garlic, mustard, and curry leaves in ghee.\n4. Serve hot with steamed rice and fresh cream (Meegada)."
    },
    {
        "id": 42, "name": "Mirchi Ka Salan", "region": "Telangana", "diet": "Vegan",
        "prep_min": 15, "cook_min": 20, "cal": 220,
        "ingredients": ["Large Bhavnagri / Banana Green Chillies", "Peanuts", "Sesame Seeds", "Dry Coconut", "Tamarind", "Ginger-Garlic"],
        "steps": "1. Slit large chillies and shallow fry in oil until blistered.\n2. Roast peanuts, sesame, dry coconut, and coriander; grind to smooth masala paste.\n3. Cook paste with tamarind juice and turmeric until fragrant.\n4. Slide in blistered chillies and simmer until gravy turns glossy."
    },
    {
        "id": 43, "name": "Pappu Charu", "region": "Andhra Pradesh", "diet": "Veg",
        "prep_min": 10, "cook_min": 25, "cal": 150,
        "ingredients": ["Toor Dal", "Drumstick", "Shallots", "Tomatoes", "Tamarind", "Sambar Powder", "Ghee Tadka"],
        "steps": "1. Cook toor dal soft and mash into smooth liquid.\n2. Boil drumstick, shallots, and tomatoes in tamarind water with turmeric and spices.\n3. Combine dal water and vegetable broth; boil rapidly until flavors concentrate.\n4. Temper with cumin, mustard, garlic, and curry leaves in pure ghee."
    },
    {
        "id": 44, "name": "Double Ka Meetha (Shahi Tukda)", "region": "Telangana", "diet": "Veg",
        "prep_min": 10, "cook_min": 25, "cal": 460,
        "ingredients": ["Milk Bread Slices", "Desi Ghee", "Full Cream Rabri Milk", "Sugar Syrup", "Saffron", "Cardamom", "Nuts"],
        "steps": "1. Deep fry crustless bread triangles in pure ghee until deep golden and crisp.\n2. Dip fried bread briefly in warm saffron-cardamom sugar syrup.\n3. Arrange in serving dish and pour thick, reduced rabri over bread.\n4. Garnish with silver vark, chopped pistachios, and slivered almonds."
    },
    {
        "id": 45, "name": "Kakaraya Vepudu (Bitter Gourd Fry)", "region": "Andhra Pradesh", "diet": "Vegan",
        "prep_min": 15, "cook_min": 20, "cal": 170,
        "ingredients": ["Thinly Sliced Bitter Gourd (Karela)", "Roasted Chana Dal & Garlic Podi", "Turmeric", "Oil"],
        "steps": "1. Slice bitter gourd thin and toss with salt and turmeric to release bitterness.\n2. Shallow fry in oil until super crisp and brown.\n3. Sprinkle generous Andhra Karapodi (garlic-chana dal spiced powder).\n4. Toss quickly and serve as a crunchy accompaniment."
    },
    {
        "id": 46, "name": "Sakinalu (Crispy Rice Rings)", "region": "Telangana", "diet": "Vegan",
        "prep_min": 30, "cook_min": 20, "cal": 290,
        "ingredients": ["Fresh Wet Rice Flour", "Sesame Seeds (Nuvvulu)", "Ajwain (Vaamu)", "Salt", "Oil for frying"],
        "steps": "1. Mix fresh pounded rice flour with plenty of white sesame seeds, ajwain, and salt.\n2. Make pliable dough with water.\n3. Skillfully pipe concentric circular spirals onto a clean cotton cloth.\n4. Deep fry in hot oil until ivory-crisp; traditional Sankranti delicacy."
    },
    {
        "id": 47, "name": "Pootharekulu (Paper Sweet)", "region": "Andhra Pradesh", "diet": "Veg",
        "prep_min": 48, "cook_min": 15, "cal": 360,
        "ingredients": ["Jaya Rice Batter Sheets", "Powdered Jaggery / Sugar", "Pure Desi Ghee", "Cardamom", "Pistachio Slivers"],
        "steps": "1. Smear ultra-thin rice batter on inverted earthenware pot over fire to form edible paper-thin film.\n2. Layer delicate rice wafer sheets with melted ghee.\n3. Sprinkle fine jaggery/sugar powder, cardamom, and chopped nuts.\n4. Fold into neat rectangular rolls like handkerchiefs."
    },
    {
        "id": 48, "name": "Bendakaya Pulusu (Okra Stew)", "region": "Andhra Pradesh", "diet": "Vegan",
        "prep_min": 10, "cook_min": 15, "cal": 130,
        "ingredients": ["Fresh Okra / Bhindi", "Tamarind Extract", "Onions", "Green Chillies", "Jaggery", "Mustard & Fenugreek Seeds"],
        "steps": "1. Sauté okra pieces in oil until non-slimy.\n2. Sauté onions and chillies; add tamarind water, turmeric, chilli powder, and jaggery.\n3. Simmer okra in tangy-sweet gravy until tender.\n4. Finish with mustard, fenugreek, and curry leaves tadka."
    },
    {
        "id": 49, "name": "Hyderabadi Marag (Mutton Soup)", "region": "Telangana", "diet": "Non-Veg",
        "prep_min": 15, "cook_min": 45, "cal": 310,
        "ingredients": ["Tender Bone-in Mutton (Shanks)", "Cashew-Almond Paste", "Full Milk/Cream", "Cardamom", "Cinnamon", "Black Pepper"],
        "steps": "1. Pressure cook mutton shanks with whole spices, ginger-garlic, and mint for 45 min until broth is rich.\n2. Sauté onions in ghee, add nut paste, black pepper, and strain in mutton broth.\n3. Add boiled meat and finish with cream.\n4. Serve rich, silky soup with naan or Sheermal at weddings."
    },
    {
        "id": 50, "name": "Bobbatlu / Obbattu (Holige)", "region": "Karnataka / Andhra", "diet": "Veg",
        "prep_min": 30, "cook_min": 20, "cal": 340,
        "ingredients": ["Chana Dal", "Organic Jaggery", "Cardamom Powder", "Maida / Chiroti Rava", "Ghee"],
        "steps": "1. Cook chana dal soft, drain, grind with jaggery and cardamom into smooth stuffing (Poornam).\n2. Make soft, stretchy dough with maida, turmeric, and oil.\n3. Encase poornam ball inside dough sheet.\n4. Roll paper-thin with oil on parchment and roast on tawa with ghee."
    }
]

class OTMBRecipeEngine:
    def __init__(self):
        self.recipes = RECIPES_DB

    def search_by_name(self, query):
        q = query.lower()
        return [r for r in self.recipes if q in r["name"].lower()]

    def search_by_ingredient(self, ingredient):
        q = ingredient.lower()
        return [r for r in self.recipes if any(q in ing.lower() for ing in r["ingredients"])]

    def filter_by_region(self, region):
        q = region.lower()
        return [r for r in self.recipes if q in r["region"].lower()]

    def filter_by_diet(self, diet):
        q = diet.lower()
        return [r for r in self.recipes if q in r["diet"].lower()]

    def format_recipe_card(self, r):
        ings = ", ".join(r["ingredients"])
        card = "=" * 60 + "\n"
        card += " 🍲 [{:02d}] {} ({}) - {}\n".format(r['id'], r['name'].upper(), r['region'], r['diet'])
        card += " ⏱ Prep: {}m | Cook: {}m | ⚡ Calories: ~{} kcal\n".format(r['prep_min'], r['cook_min'], r['cal'])
        card += "-" * 60 + "\n"
        card += " 🛒 Key Ingredients:\n    {}\n\n".format(ings)
        card += " 👩‍🍳 Method & Steps:\n"
        for line in r["steps"].split("\n"):
            card += "    {}\n".format(line)
        card += "=" * 60 + "\n"
        return card

def run_recipe_app():
    engine = OTMBRecipeEngine()
    print("=" * 60)
    print(" 🌶 OTMB 50 FAMOUS SOUTH INDIAN FOOD RECIPES (RP2040 ENGINE)")
    print("=" * 60)
    print(" Loaded {} authentic recipes across KA, TN, KL, AP, TS.".format(len(engine.recipes)))
    print(" Total recipe database ready for offline instant search.")

if __name__ == "__main__":
    run_recipe_app()
