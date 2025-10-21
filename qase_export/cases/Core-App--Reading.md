# Core App & Reading

_Suite ID: 12_

| ID | Title | Priority | Status |
|---:|-------|---------|--------|
| C2 | Initial app load |  |  |
| C3 | Open version selection modal |  |  |
| C4 | Open book selection modal |  |  |
| C5 | Book Chapter verse navigation |  |  |

## Details
### C2: Initial app load

- **Priority:** 0
- **Severity:** 4
- **Status:** 0
- **Type:** 2
- **Behavior:** 1
- **Layer:** 1
- **Tags:** —

**Preconditions**

—

**Steps**

```
1. Open /. (Navigate to Home page)
   - Expected: No http error displayed, no console error
2. Verify Menu options list (Home, Study & Reflect, Communities, Contact, Account)
3. Verify Hero section's h1 element and "Get Started" button
4. Verify description cards (About, Read the bible, Study & Reflect, Community)
```

**Expected result**

—

### C3: Open version selection modal

- **Priority:** 0
- **Severity:** 4
- **Status:** 0
- **Type:** 1
- **Behavior:** 1
- **Layer:** 0
- **Tags:** —

**Preconditions**

—

**Steps**

```
1. Navigate to home page (/)
2. Click "Study & Reflect" option from menu
3. Navigate to /study
4. Click on the version dropdown menu with "ASV" place holder
5. Verify Version Modal components
   - Expected: Version filter input box should be enabled, and list of versions should be categorized by language
```

**Expected result**

—

### C4: Open book selection modal

- **Priority:** 0
- **Severity:** 4
- **Status:** 0
- **Type:** 1
- **Behavior:** 1
- **Layer:** 0
- **Tags:** —

**Preconditions**

—

**Steps**

```
1. Navigate to home page (/)
2. Click "Study & Reflect" option from menu
3. Navigate to /study
4. Click on the books dropdown menu with "Genesis" place holder
5. Verify Book Modal components
   - Expected: Book filter input box should be enabled, and list of books should be in ascending order
```

**Expected result**

—

### C5: Book Chapter verse navigation

- **Priority:** 0
- **Severity:** 4
- **Status:** 0
- **Type:** 1
- **Behavior:** 1
- **Layer:** 1
- **Tags:** —

**Preconditions**

—

**Steps**

```
1. Navigate to home (/)
2. Navigate to "Study and Reflect" (/study)
3. Click on the book selector drop down menu with place holder "Genesis"
4. Select John -> 3 -> 16
5. Verify top display area
   - Expected: Top shows “John 3:16”; the verse is focused and readable.
```

**Expected result**

—
