from emails.parser import USPTOParser

html = """
<html>
<body>
<p>Customer Number: 203246</p>

<table border="1">
<tr>
    <th>Application</th>
    <th>Document</th>
    <th>Mailroom Date</th>
</tr>
<tr>
    <td>18528497</td>
    <td>CTNF</td>
    <td>03/25/2026</td>
</tr>
<tr>
    <td>18528498</td>
    <td>892</td>
    <td>03/25/2026</td>
</tr>
<tr>
    <td>18528499</td>
    <td>1449</td>
    <td>03/25/2026</td>
</tr>
</table>

</body>
</html>
"""

parser = USPTOParser()
result = parser.parse(html)

print("✅ Parsed Output:")
for r in result:
    print(r)