import express, { Request, Response } from "express";

// ==== Type Definitions, feel free to add or modify ==========================
interface cookbookEntry {
  name: string;
  type: string;
}

interface requiredItem {
  name: string;
  quantity: number;
}

interface recipe extends cookbookEntry {
  requiredItems: requiredItem[];
}

interface ingredient extends cookbookEntry {
  cookTime: number;
}

// =============================================================================
// ==== HTTP Endpoint Stubs ====================================================
// =============================================================================
const app = express();
app.use(express.json());

// Store your recipes here!
const cookbook: Record<string, recipe | ingredient> = {};

// Task 1 helper (don't touch)
app.post("/parse", (req:Request, res:Response) => {
  const { input } = req.body;

  const parsed_string = parse_handwriting(input)
  if (parsed_string == null) {
    res.status(400).send("this string is cooked");
    return;
  } 
  res.json({ msg: parsed_string });
  return;
  
});

// [TASK 1] ====================================================================
// Takes in a recipeName and returns it in a form that 
const parse_handwriting = (recipeName: string): string | null => {
  recipeName = recipeName.replace("_", " ").replace("-", " ");

  // regex
  recipeName = recipeName.replace(/[^a-zA-Z\s]/g, ""); // a-z, A-Z, or space (\s) with empty string

	const words: string[] = recipeName.trim().split(/\s+/);

	if (words == null) {
    return null;
	
  }

  return words.map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(" ");
}

// [TASK 2] ====================================================================
// Endpoint that adds a CookbookEntry to your magical cookbook
app.post("/entry", (req:Request, res:Response) => {
  const data = req.body();

	const type: string = data.type;
	const name: string = data.name;
  let new_entry: recipe | ingredient;

	if (name in cookbook) {
    return res.status(400).send("Error: entry already exists! (entry names must be unique)");
  }
	
	if (type == "recipe") {
    const visited_items = new Set<string>();
    const approved_items: requiredItem[] = [];

    const items: any[] = data.requiredItems ?? [];

		for (const item of items) {
      const item_name: string = item.name;
      const item_quantity: number = item.quantity;
      if (visited_items.has(item_name)) {
        return res.status(400).send("Error: duplicated required item in recipe!");
      }

      visited_items.add(item_name);
      approved_items.push({
        name: item_name,
        quantity: item_quantity
      });
    }

    new_entry = {
      name: name,
      type: "recipe",
      requiredItems: approved_items
    };
  } else if (type == "ingredient") {
    const cook_time: number = data.cookTime;
		
		if (cook_time < 0) {
      return res.status(400).send("Error: invalid cook time! (cook time >= 0)");
    }
		
		new_entry = {
      name: name,
      type: "ingredient",
      cookTime: cook_time
    };

  } else {
    return res.status(400).send("Error: invalid type! (not recipe or ingredient)");
  }
	
	cookbook[name] = new_entry;
	
	return res.status(200).json({});

});

// [TASK 3] ====================================================================
// Endpoint that returns a summary of a recipe that corresponds to a query name
app.get("/summary", (req:Request, res:Request) => {
  // TODO: implement me
  res.status(500).send("not yet implemented!")

});

// =============================================================================
// ==== DO NOT TOUCH ===========================================================
// =============================================================================
const port = 8080;
app.listen(port, () => {
  console.log(`Running on: http://127.0.0.1:8080`);
});
