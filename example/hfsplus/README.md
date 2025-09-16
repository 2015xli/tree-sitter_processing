Bug in tree-sitter-cpp: using CPP parser still finishes parsing the hfsplus_fs.h

When it meets the following code snippet, it parses the "class" as class_specifier.

static inline enum hfsplus_btree_mutex_classes
hfsplus_btree_lock_class(struct hfs_btree *tree)
{
        enum hfsplus_btree_mutex_classes class;

        switch (tree->cnid) {
        case HFSPLUS_CAT_CNID:
                class = CATALOG_BTREE_MUTEX;
                break;
        case HFSPLUS_EXT_CNID:
                class = EXTENTS_BTREE_MUTEX;
                break;
        case HFSPLUS_ATTR_CNID:
                class = ATTR_BTREE_MUTEX;
                break;
        default:
                BUG();
        }
        return class;
}
 
