import styles from "../styles/App.module.css";

type SelectTypeMenuProps = {
  name: string;
  selectList: string[];
  state: string;
  setState: React.Dispatch<React.SetStateAction<string>>;
};

export default function SelectTypeMenu(props: SelectTypeMenuProps) {
  const { name, selectList, state, setState } = props;
  return (
    <div className={styles.formGroup}>
      <label>{name}</label>
      <select value={state} onChange={(e) => setState(e.target.value)}>
        {selectList.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
    </div>
  );
}
