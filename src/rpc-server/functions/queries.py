from lxml import etree
from database.database import Database

def fetch_brands():
    database = Database()
    result_brands = []

    results = database.selectAll("SELECT unnest(xpath('//Brands/Brand/@name', xml)) as result FROM imported_documents WHERE deleted_on IS NULL")
    database.disconnect()

    for brand in results:
        if not brand in result_brands:
            result_brands.append(brand)

    return result_brands

def fetch_models():
    database = Database()
    result_models = []

    results = database.selectAll("SELECT unnest(xpath('//Brands/Brand/Models/Model/@name', xml)) as result FROM imported_documents WHERE deleted_on IS NULL")
    database.disconnect()

    for model in results:
        if not model in result_models:
            result_models.append(model)

    return result_models


def fetch_market_categories():
    database = Database()
    results_categories = []
    results = database.selectAll("SELECT unnest(xpath('//Categories/market_category/@Name', xml)) as result FROM imported_documents WHERE deleted_on IS NULL")
    database.disconnect()

    for category in results:
        if not category in results_categories:
            results_categories.append(category)

    return results_categories

def fetch_most_valuable_cars():
    database = Database()

    query = """
    WITH vehicle_data AS ( SELECT
            unnest(xpath('//Vehicles/Car/@id', xml))::text as id,
            unnest(xpath('//Vehicles/Car/@year', xml))::text as year,
            unnest(xpath('//Vehicles/Car/@brand_ref', xml))::text as brand_ref,
            unnest(xpath('//Vehicles/Car/@model_ref', xml))::text as model_ref,
            unnest(xpath('//Data/Vehicles/Car/Msrp/@value', xml))::text as msrp FROM imported_documents WHERE deleted_on IS NULL ),
    
    model_data AS 
    
    (SELECT unnest(xpath('//Brands/Brand/Models/Model/@id', xml))::text as model_id, unnest(xpath('//Brands/Brand/Models/Model/@name', xml))::text as model_name FROM imported_documents WHERE deleted_on IS NULL)
    
    SELECT car.id, car.year, COALESCE(brand.name, 'N/A') as brand_name, COALESCE(model.model_name, 'N/A') as model_name, car.msrp FROM vehicle_data car
    
    LEFT JOIN(SELECT unnest(xpath('//Brands/Brand/@id', xml))::text as brand_id, unnest(xpath('//Brands/Brand/@name', xml))::text as name FROM imported_documents WHERE deleted_on IS NULL) brand ON car.brand_ref = brand.brand_id
    
    LEFT JOIN model_data model ON car.model_ref = model.model_id 
    
    WHERE car.msrp IS NOT NULL 
    
    ORDER BY car.msrp::numeric DESC LIMIT 20;
    """

    results = database.selectAllArray(query)
    database.disconnect()

    query_result = [
        {
            "id": car.get("id", "N/A"),
            "year": car.get("year", "N/A"),
            "brand_name": car.get("brand_name", "N/A"),
            "model_name": car.get("model_name", "N/A"),
            "msrp": car.get("msrp", "N/A"),
        }
        for car in results
    ]

    return query_result

def fetch_models_by_brand(brand_name):
    database = Database()
    result_models = []


    query = f"""
    SELECT unnest(xpath('//Brand[@name="{brand_name}"]/Models/Model/@name', xml)) as result
    FROM imported_documents
    WHERE deleted_on IS NULL;
    """

    results = database.selectAll(query)
    database.disconnect()

    for model in results:
        if not model in result_models:
            result_models.append(model)

    return result_models

def fetch_vehicles_by_category(category):
    database = Database()

    query = f"""
    WITH vehicle_data AS (
        SELECT
            unnest(xpath('//Vehicles/Car/@id', xml))::text as id,
            unnest(xpath('//Vehicles/Car/@year', xml))::text as year,
            unnest(xpath('//Vehicles/Car/@brand_ref', xml))::text as brand_ref,
            unnest(xpath('//Vehicles/Car/@model_ref', xml))::text as model_ref,
            unnest(xpath('//Data/Vehicles/Car/Msrp/@value', xml))::text as msrp
        FROM imported_documents
        WHERE deleted_on IS NULL
    ),
    model_data AS (
        SELECT
            unnest(xpath('//Brands/Brand/Models/Model/@id', xml))::text as model_id,
            unnest(xpath('//Brands/Brand/Models/Model/@name', xml))::text as model_name
        FROM imported_documents
        WHERE deleted_on IS NULL
    )

    SELECT
        car.id,
        car.year,
        COALESCE(brand.name, 'N/A') as brand_name,
        COALESCE(model.model_name, 'N/A') as model_name,
        car.msrp
    FROM vehicle_data car
    LEFT JOIN (
        SELECT
            unnest(xpath('//Brands/Brand/@id', xml))::text as brand_id,
            unnest(xpath('//Brands/Brand/@name', xml))::text as name
        FROM imported_documents
        WHERE deleted_on IS NULL
    ) brand ON car.brand_ref = brand.brand_id
    LEFT JOIN model_data model ON car.model_ref = model.model_id
    WHERE car.msrp IS NOT NULL;
    """

    results = database.selectAllArray(query)
    database.disconnect()

    query_result = [
        {
            "id": car.get("id", "N/A"),
            "year": car.get("year", "N/A"),
            "brand_name": car.get("brand_name", "N/A"),
            "model_name": car.get("model_name", "N/A"),
            "msrp": car.get("msrp", "N/A"),
        }
        for car in results
    ]

    return query_result

def fetch_category_statistics(brand_name):
    database = Database()

    query = f"""
    SELECT
        category.category_name,
        COUNT(vehicle.id) AS vehicle_count
    FROM
        unnest(xpath(
            '//Car[./Market_Categories/market_category/@ref = (SELECT unnest(xpath(\'//Brand[@name="{brand_name}"]/Models/Model/@name\', xml)) FROM imported_documents WHERE deleted_on IS NULL)]',
            xml
        )) AS category(category_name),
        vehicles AS vehicle
    WHERE
        category.category_name IS NOT NULL
    GROUP BY
        category.category_name;
    """

    results = database.selectAll(query)
    database.disconnect()

    category_statistics = [
        {
            "category": result.get("category_name", "N/A"),
            "vehicle_count": result.get("vehicle_count", 0)
        }
        for result in results
    ]

    return category_statistics