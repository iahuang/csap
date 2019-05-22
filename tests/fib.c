int result;

int main()
{
    int i, n, t1 = 0, t2 = 1, nextTerm;

    n = 10;

    for (i = 1; i <= n; ++i)
    {
        nextTerm = t1 + t2;
        t1 = t2;
        t2 = nextTerm;
    }
    result = t1;
    return 0;
}