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

`branch` field added to differentiate branch-specific entries. Also added `company` field in **Branch** handle `set_query` in **Journal Entry**

#### License

MIT
