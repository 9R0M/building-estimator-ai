import styles from "../styles/AllInOneEstimatePage.module.css";

type SelectTypeMenuProps = {
  label: string;
  selectList: {label: string; value: string}[];
  value: string;
  onChange: React.Dispatch<React.SetStateAction<string>>;
};

export default function SelectTypeMenu(props: SelectTypeMenuProps) {
  const { label, selectList,  value, onChange } = props;
  return (
    <div className={styles.formGroup}>
      <label>{label}</label>
      <select value= {value} onChange={(e) => onChange(e.target.value)}>
        {selectList.map((s) => (
          <option key={s.label} label={s.label} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
    </div>
  );
}
