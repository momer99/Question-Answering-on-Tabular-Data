import csv

# Data for the CSV
data = [
    ['Month', 'Product', 'Sales', 'Revenue'],
    ['January', 'Product A', 150, 4500],
    ['January', 'Product B', 200, 6000],
    ['January', 'Product C', 180, 5400],
    ['February', 'Product A', 160, 4800],
    ['February', 'Product B', 210, 6300],
    ['February', 'Product C', 190, 5700],
    ['March', 'Product A', 170, 5100],
    ['March', 'Product B', 220, 6600],
    ['March', 'Product C', 200, 6000],
    ['April', 'Product A', 180, 5400],
    ['April', 'Product B', 230, 6900],
    ['April', 'Product C', 210, 6300],
    ['May', 'Product A', 190, 5700],
    ['May', 'Product B', 240, 7200],
    ['May', 'Product C', 220, 6600],
    ['June', 'Product A', 200, 6000],
    ['June', 'Product B', 250, 7500],
    ['June', 'Product C', 230, 6900],
    ['July', 'Product A', 210, 6300],
    ['July', 'Product B', 260, 7800],
    ['July', 'Product C', 240, 7200],
    ['August', 'Product A', 220, 6600],
    ['August', 'Product B', 270, 8100],
    ['August', 'Product C', 250, 7500],
    ['September', 'Product A', 230, 6900],
    ['September', 'Product B', 280, 8400],
    ['September', 'Product C', 260, 7800],
    ['October', 'Product A', 240, 7200],
    ['October', 'Product B', 290, 8700],
    ['October', 'Product C', 270, 8100],
    ['November', 'Product A', 250, 7500],
    ['November', 'Product B', 300, 9000],
    ['November', 'Product C', 280, 8400],
    ['December', 'Product A', 260, 7800],
    ['December', 'Product B', 310, 9300],
    ['December', 'Product C', 290, 8700],
    ['January', 'Product A', 150, 4500],
    ['January', 'Product B', 200, 6000],
    ['January', 'Product C', 180, 5400],
    ['February', 'Product A', 160, 4800],
    ['February', 'Product B', 210, 6300],
    ['February', 'Product C', 190, 5700],
    ['March', 'Product A', 170, 5100],
    ['March', 'Product B', 220, 6600],
    ['March', 'Product C', 200, 6000],
]

# Write data to CSV
with open('sales_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print("CSV file 'sales_data.csv' created successfully!")