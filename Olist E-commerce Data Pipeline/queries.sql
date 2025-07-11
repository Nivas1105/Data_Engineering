-- Total Sales by Product Category
SELECT
    p.product_category_name,
    SUM(f.price) as total_revenue
FROM fct_order_items f
JOIN dim_products p ON f.product_id = p.product_id
WHERE p.product_category_name IS NOT NULL
GROUP BY p.product_category_name
ORDER BY total_revenue DESC
LIMIT 10;
/*
product_category_name |	total_revenue
beleza_saude	1290883.52	
relogios_presentes	1245783.11	
cama_mesa_banho	1095770.05	
esporte_lazer	1022489.29	
informatica_acessorios	944992.54	
moveis_decoracao	765336.72	
utilidades_domesticas	664226.76	
cool_stuff	655820.4	
automotivo	608914.3	
ferramentas_jardim	515987.77	

*/

-- Average Review Score by Seller State
SELECT
    s.seller_state,
    AVG(f.review_score) as average_review_score
FROM fct_order_items f
JOIN dim_sellers s ON f.seller_id = s.seller_id
GROUP BY s.seller_state
ORDER BY average_review_score DESC;
/*
seller_state |	average_review_score
DF	4	
MT	4	
SP	4	
PI	4	
MS	4	
SC	4	
PE	4	
RN	4	
PR	4	
PA	4	
MG	4	
BA	4	
RS	4	
RJ	4	
GO	4	
CE	4	
MA	3	
RO	3	
SE	3	
PB	3	
ES	3	
AM	2	
AC	1	
*/

-- Overall Business Health Summary
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT seller_id) AS total_sellers,
    SUM(price) AS total_revenue,
    AVG(payment_value) AS average_order_value,
    AVG(review_score) AS average_review_score
FROM public.fct_order_items;
/*
total_orders	total_customers	total_sellers	total_revenue	average_order_value	average_review_score
97916	97916	3090	14141001.32	172.06	4	

*/
-- Top 10 Best-Selling Product Categories by Revenue
SELECT
    p.product_category_name,
    SUM(f.price) AS total_revenue,
    COUNT(f.order_id) AS number_of_orders
FROM public.fct_order_items f
JOIN public.dim_products p ON f.product_id = p.product_id
WHERE p.product_category_name IS NOT NULL
GROUP BY p.product_category_name
ORDER BY total_revenue DESC
LIMIT 10;
/*
product_category_name	total_revenue	number_of_orders
beleza_saude	1290883.52	9944	
relogios_presentes	1245783.11	6161	
cama_mesa_banho	1095770.05	11847	
esporte_lazer	1022489.29	8942	
informatica_acessorios	944992.54	8105	
moveis_decoracao	765336.72	8743	
utilidades_domesticas	664226.76	7331	
cool_stuff	655820.4	3964	
automotivo	608914.3	4356	
ferramentas_jardim	515987.77	4558	

*/
-- Average Freight Value vs. Product Weight by Category
SELECT
    p.product_category_name,
    AVG(f.freight_value) AS average_freight_cost,
    AVG(p.product_weight_g) AS average_product_weight_grams
FROM public.fct_order_items f
JOIN public.dim_products p ON f.product_id = p.product_id
WHERE p.product_category_name IS NOT NULL AND p.product_weight_g > 0
GROUP BY p.product_category_name
ORDER BY average_freight_cost DESC;
/*
product_category_name	average_freight_cost	average_product_weight_grams
pcs	47.24	6957	
eletrodomesticos_2	46.03	9888	
moveis_quarto	44.18	10124	
moveis_cozinha_area_de_servico_jantar_e_jardim	42.56	8670	
moveis_colchao_e_estofado	41.77	8446	
moveis_escritorio	40.02	11281	
portateis_casa_forno_e_cafe	36.98	5176	
moveis_sala	35.53	8099	
sinalizacao_e_seguranca	32.7	3883	
industria_comercio_e_negocios	29.45	6645	
agro_industria_e_comercio	27.64	4248	
malas_acessorios	27.63	5690	
instrumentos_musicais	27.32	3119	
la_cuisine	25.78	3763	
construcao_ferramentas_iluminacao	24.79	3374	
eletroportateis	23.98	3037	
ferramentas_jardim	23.08	2910	
casa_construcao	22.84	3161	
climatizacao	22.66	4113	
bebes	22.38	3260	
construcao_ferramentas_jardim	22.27	2277	
construcao_ferramentas_construcao	22.14	3127	
cool_stuff	21.96	2509	
automotivo	21.83	2600	
utilidades_domesticas	20.98	3198	
moveis_decoracao	20.73	2677	
portateis_cozinha_e_preparadores_de_alimentos	20.65	2838	
seguros_e_servicos	20.61	812	
artigos_de_natal	20.32	1885	
pet_shop	20.29	3021	
dvds_blu_ray	20.18	600	
construcao_ferramentas_seguranca	20.06	791	
construcao_ferramentas_ferramentas	19.89	1195	
esporte_lazer	19.49	1746	
eletrodomesticos	19.23	1911	
casa_conforto	19.2	3065	
artigos_de_festas	19.15	2134	
artes	19.14	1545	
fashion_esporte	19.1	335	
brinquedos	18.96	1848	
informatica_acessorios	18.93	899	
beleza_saude	18.9	1042	
papelaria	18.64	2744	
fashion_calcados	18.55	1024	
cama_mesa_banho	18.38	2121	
musica	17.88	1849	
market_place	17.59	1117	
telefonia_fixa	17.53	561	
consoles_games	17.46	453	
cine_foto	17.17	1132	
relogios_presentes	16.82	579	
eletronicos	16.78	797	
livros_interesse_geral	16.68	765	
alimentos_bebidas	16.43	1099	
cds_dvds_musicais	16.07	550	
livros_tecnicos	16.02	1009	
fashion_roupa_masculina	15.99	570	
perfumaria	15.79	475	
telefonia	15.73	262	
audio	15.69	1207	
fashion_bolsas_e_acessorios	15.68	393	
artes_e_artesanato	15.42	1369	
bebidas	15.1	1024	
pc_gamer	14.86	1978	
tablets_impressao_imagem	14.85	292	
fraldas_higiene	14.7	665	
flores	14.63	1901	
fashion_underwear_e_moda_praia	14.5	269	
alimentos	14.35	662	
casa_conforto_2	13.42	837	
livros_importados	13.05	625	
fashion_roupa_feminina	12.92	553	
fashion_roupa_infanto_juvenil	11.93	265	
*/

-- Top 10 Cities by Number of Orders
SELECT
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT f.order_id) AS number_of_orders
FROM public.fct_order_items f
JOIN public.dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.customer_city, c.customer_state
ORDER BY number_of_orders DESC
LIMIT 10;
/*
customer_city	customer_state	number_of_orders
sao paulo	SP	15291	
rio de janeiro	RJ	6749	
belo horizonte	MG	2731	
brasilia	DF	2106	
curitiba	PR	1501	
campinas	SP	1413	
porto alegre	RS	1364	
salvador	BA	1213	
guarulhos	SP	1166	
sao bernardo do campo	SP	926	
*/
-- Customer Purchase Frequency
SELECT
    c.customer_unique_id,
    COUNT(DISTINCT f.order_id) as total_orders
FROM public.fct_order_items f
JOIN public.dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.customer_unique_id
HAVING COUNT(DISTINCT f.order_id) > 1 
ORDER BY total_orders DESC
LIMIT 20;
/*
customer_unique_id	total_orders
8d50f5eadf50201ccdcedfb9e2ac8455	16	
3e43e6105506432c953e165fb2acf44c	9	
ca77025e7201e3b30c44b472ff346268	7	
6469f99c1f9dfae7733b25662e7f1782	7	
1b6c7548a2a1f9037c1fd3ddfed95f33	7	
dc813062e0fc23409cd255f7f53c7074	6	
63cfc61cee11cbe306bff5857d00bfe4	6	
12f5d6e1cbf93dafd9dcc19095df0b3d	6	
47c1a3033b8b77b3ab6e109eb4d5fdf3	6	
f0e310a6839dce9de1638e0fe5ab282a	6	
394ac4de8f3acb14253c177f0e15bc58	5	
56c8638e7c058b98aae6d74d2dd6ea23	5	
5e8f38a9a1c023f3db718edcf926a2db	5	
4e65032f1f574189fb793bac5a867bbc	5	
b4e4f24de1e8725b74e4a1f4975116ed	5	
35ecdf6858edc6427223b64804cf028e	5	
fe81bb32c243a86b2f86fbf053fe6140	5	
74cb1ad7e6d5674325c1f99b5ea30d82	5	
de34b16117594161a6a89c50b289d35a	5	
08e5b38d7948d37fbb2a59fc5e175ab1	4	
*/
-- Monthly Sales Revenue Trend
SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::DATE AS sales_month,
    SUM(payment_value) AS monthly_revenue,
    COUNT(DISTINCT order_id) AS monthly_orders
FROM public.fct_order_items
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY sales_month
ORDER BY sales_month;
/*
sales_month	monthly_revenue	monthly_orders
2016-09-01	347.52	2	
2016-10-01	72871.74	303	
2016-12-01	19.62	1	
2017-01-01	188107.24	779	
2017-02-01	344822.39	1722	
2017-03-01	521299.33	2621	
2017-04-01	501333.64	2374	
2017-05-01	724696.48	3626	
2017-06-01	602247.64	3192	
2017-07-01	735468.88	3934	
2017-08-01	825555.66	4261	
2017-09-01	1017433.53	4209	
2017-10-01	1023832.03	4530	
2017-11-01	1579407.32	7390	
2017-12-01	1031286.23	5567	
2018-01-01	1403107.09	7154	
2018-02-01	1305633.51	6639	
2018-03-01	1468770.91	7125	
2018-04-01	1487962.23	6878	
2018-05-01	1497302.45	6819	
2018-06-01	1293386.96	6134	
2018-07-01	1338896.51	6228	
2018-08-01	1223973.33	6427	
2018-09-01	166.46	1	
*/
-- Sales by Day of the Week
SELECT
    CASE EXTRACT(dow FROM order_purchase_timestamp)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    SUM(payment_value) AS total_revenue,
    AVG(payment_value) AS average_revenue_per_order
FROM public.fct_order_items
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY EXTRACT(dow FROM order_purchase_timestamp)
ORDER BY EXTRACT(dow FROM order_purchase_timestamp);
/*
day_of_week	total_revenue	average_revenue_per_order
Sunday	2272718.01	163.11	
Monday	3284844.73	172.55	
Tuesday	3309552.85	173.71	
Wednesday	3088972.25	168.8	
Thursday	3089806.98	175.87	
Friday	3007515.23	179.43	
Saturday	2134518.65	168.33	
*/