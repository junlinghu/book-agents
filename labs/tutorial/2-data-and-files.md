# Tutorial 2. Shop data and files

## Motivation

A return rule is one fact. Running a shop needs two more. Someone at the counter asks what is running low, and someone asks whether a carton of milk can be shipped. The policy file from the first tutorial does not hold a shelf count, and a count does not hold the shipping rule. This lesson gives the concierge a way to read the shop’s own documents and the shelf, and to answer from those readings.

## What this tutorial is about

This lesson adds two sensors beside the policy tool you already have. A sensor is a tool that reports the world and leaves it unchanged. One sensor reads a shop document, the policy or the FAQ, and only from the folder those documents live in. The other reads the shelf, which is a small database of what is on hand.

You will learn three habits. The file tool stays inside the shop folder. The shelf tool accepts a plain question, such as which items are low, while the program writes the database query. One reply may need both tools. You will also learn the shop’s meaning of low stock: the amount on hand has fallen to the reorder point or below it. How many units would fill the shelf is a different number, and this lesson keeps the two apart.

## How you will get there

The notebook keeps the return-rule tool and registers the document tool and the shelf tool. You ask which items are low, and whether oat milk can ship. The model requests the tools. The harness reads the allowed file and the shelf, then the model writes an answer from those results.

You will compare the printed answer with the document and the shelf, so a number or a shipping rule has a source you can point to. The hands-on steps are in the notebook [2-data-and-files](2-data-and-files.ipynb).

## Additional things

A file tool with a wide path is an open door. The check in this lesson is the same one Chapter 2 uses: the path has to stay inside the shop documents. A request that climbs out of that folder comes back as an error the model can read.

A shelf tool that lets the model write the query is a different tool from the one in this notebook. Here the model names the question. The program chooses the statement. That split is what keeps a curious question from becoming a change to the database.

The first tutorial’s question still runs at the end of this notebook, so you can see the earlier tool survive the addition. Later lessons put these calls inside a loop, because a real counter question often needs more than one exchange.

The café in these files is fictional. The documents and the shelf match the other labs in this book. Leave private files alone.

## Sources and references

- [Chapter 2: The Agent Loop](../../chapters/ch02-your-first-loop/README.md). The path check is [labs/common/tools.py](../common/tools.py). The shop documents are in [labs/ch02-your-first-loop/docs](../ch02-your-first-loop/docs).
- [Chapter 4: Tools and Sensors](../../chapters/ch04-tools-and-sensors/README.md), and the shelf lab [sql_tools.py](../ch04-tools-and-sensors/sql_tools.py).
- The previous lecture is [1-using-tool.md](1-using-tool.md). The series map is in [README.md](README.md).
