## PSD SELF Customization

Customizations for PSD SELF

### Batch

`name` is set using `expiry_date` and `item_code`. Customization should deprecate once ERPNext core **Batch** changes are pushedto stable.

### Naming Series

Custom series for DocTypes

- **Sales Invoice**
- **Payment Entry**

They are auto-selected based on **Company** by creating **Naming Series** entry similar to this format `PE-[company_abbr]/.YY.-` where `[company_abbr]` should be replaced with existing ones.

### Journal Entry

`branch` field added to differentiate branch-specific entries. Also added `company` field in **Branch** handle `set_query` in **Journal Entry**.

### Sales Invoice

`gym_subscription` field added to reference **Gym Subscription**.

### Item

Add a menu item to generate EAN13 barcodes with a Dashboard section to render and download a barcoded item label.

`is_membership_item` and `is_subscription_item` specify **Items** used by **Gym Memberships** and **Gym Subscriptions** respectively. Both these fields are used by **Gym Subscription**.

`can_be_lifetime` flags **Items** that can have lifetime validity.

`gym_parent_items` added to hold info about **Item** heirarchy. This heirarchy will be used to check for existence of parent items before creating new **Gym Subscription**

#### License

MIT
